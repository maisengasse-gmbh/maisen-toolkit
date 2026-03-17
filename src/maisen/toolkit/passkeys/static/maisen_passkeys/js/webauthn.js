/**
 * WebAuthn-Helpers für Passkey-Registrierung und -Authentifizierung.
 *
 * Verwendung:
 *   await registerPasskey(beginUrl, completeUrl, csrfToken);
 *   await authenticatePasskey(beginUrl, completeUrl, csrfToken);
 */

function b64urlEncode(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function b64urlDecode(str) {
    str = str.replace(/-/g, "+").replace(/_/g, "/");
    while (str.length % 4) str += "=";
    const binary = atob(str);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

/**
 * Startet und beendet die Passkey-Registrierung.
 * @param {string} beginUrl - URL für register/begin/
 * @param {string} completeUrl - URL für register/complete/
 * @param {string} csrfToken - CSRF-Token
 * @param {string} name - Name für den Passkey
 * @returns {Promise<object>} - Server-Antwort
 */
async function registerPasskey(beginUrl, completeUrl, csrfToken, name) {
    // 1. Begin – Optionen vom Server holen
    const beginResp = await fetch(beginUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ name: name || "" }),
    });

    if (!beginResp.ok) {
        const err = await beginResp.json();
        throw new Error(err.error || "Registrierung konnte nicht gestartet werden.");
    }

    const options = await beginResp.json();

    // PublicKeyCredentialCreationOptions vorbereiten
    const publicKey = options.publicKey;
    publicKey.challenge = b64urlDecode(publicKey.challenge);
    publicKey.user.id = b64urlDecode(publicKey.user.id);
    if (publicKey.excludeCredentials) {
        publicKey.excludeCredentials = publicKey.excludeCredentials.map(function(c) {
            return Object.assign({}, c, { id: b64urlDecode(c.id) });
        });
    }

    // 2. Browser-API aufrufen
    const credential = await navigator.credentials.create({ publicKey: publicKey });

    // 3. Complete – Ergebnis an Server senden (fido2 2.x Format)
    const regRawId = b64urlEncode(credential.rawId);
    const completeBody = {
        id: regRawId,
        rawId: regRawId,
        type: credential.type,
        response: {
            clientDataJSON: b64urlEncode(credential.response.clientDataJSON),
            attestationObject: b64urlEncode(credential.response.attestationObject),
        },
    };

    const completeResp = await fetch(completeUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(completeBody),
    });

    if (!completeResp.ok) {
        const err = await completeResp.json();
        throw new Error(err.error || "Registrierung fehlgeschlagen.");
    }

    return await completeResp.json();
}

/**
 * Startet und beendet die Passkey-Authentifizierung.
 * @param {string} beginUrl - URL für authenticate/begin/
 * @param {string} completeUrl - URL für authenticate/complete/
 * @param {string} csrfToken - CSRF-Token
 * @returns {Promise<object>} - Server-Antwort
 */
async function authenticatePasskey(beginUrl, completeUrl, csrfToken) {
    // 1. Begin – Optionen vom Server holen
    const beginResp = await fetch(beginUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: "{}",
    });

    if (!beginResp.ok) {
        const err = await beginResp.json();
        throw new Error(err.error || "Authentifizierung konnte nicht gestartet werden.");
    }

    const options = await beginResp.json();

    // PublicKeyCredentialRequestOptions vorbereiten
    const publicKey = options.publicKey;
    publicKey.challenge = b64urlDecode(publicKey.challenge);
    if (publicKey.allowCredentials) {
        publicKey.allowCredentials = publicKey.allowCredentials.map(function(c) {
            return Object.assign({}, c, { id: b64urlDecode(c.id) });
        });
    }

    // 2. Browser-API aufrufen
    const assertion = await navigator.credentials.get({ publicKey: publicKey });

    // 3. Complete – Ergebnis an Server senden (fido2 2.x Format)
    const rawId = b64urlEncode(assertion.rawId);
    const completeBody = {
        id: rawId,
        rawId: rawId,
        type: assertion.type,
        response: {
            clientDataJSON: b64urlEncode(assertion.response.clientDataJSON),
            authenticatorData: b64urlEncode(assertion.response.authenticatorData),
            signature: b64urlEncode(assertion.response.signature),
        },
    };

    const completeResp = await fetch(completeUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(completeBody),
    });

    if (!completeResp.ok) {
        const err = await completeResp.json();
        throw new Error(err.error || "Authentifizierung fehlgeschlagen.");
    }

    return await completeResp.json();
}
