import translate from 'google-translate-api-x';
import settings from '../agent/settings.js';

async function translateWithRetry(text, options, maxRetries = 3) {
    let lastError;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Translation timeout')), 20000)
            );
            
            const translation = await Promise.race([
                translate(text, { ...options, forceTo: true }),
                timeoutPromise
            ]);
            
            return translation.text || text;
        } catch (error) {
            lastError = error;
            console.warn(`Translation attempt ${attempt + 1} failed:`, error.message);
            if (attempt < maxRetries - 1) {
                const delay = Math.pow(2, attempt) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    console.error('All translation attempts failed:', lastError);
    return text;
}

export async function handleTranslation(message) {
    let preferred_lang = String(settings.language).toLowerCase();
    if (!preferred_lang || preferred_lang === 'en' || preferred_lang === 'english')
        return message;
    try {
        return await translateWithRetry(message, { to: preferred_lang });
    } catch (error) {
        console.error('Error translating message:', error);
        return message;
    }
}

export async function handleEnglishTranslation(message) {
    let preferred_lang = String(settings.language).toLowerCase();
    if (!preferred_lang || preferred_lang === 'en' || preferred_lang === 'english')
        return message;
    try {
        return await translateWithRetry(message, { to: 'english' });
    } catch (error) {
        console.error('Error translating message:', error);
        return message;
    }
}
