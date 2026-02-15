import settings from '../settings.js';

export function addBrowserViewer(bot, count_id) {
    if (settings.render_bot_view) {
        import('prismarine-viewer').then((prismarineViewer) => {
            try {
                const mineflayerViewer = prismarineViewer.mineflayer;
                mineflayerViewer(bot, { port: 3000+count_id, firstPerson: true, });
                console.log(`Bot view started successfully on port ${3000+count_id}`);
            } catch (error) {
                console.warn('Failed to start bot view:', error.message);
                console.warn('Bot view will be disabled, but bot will continue to work');
            }
        }).catch((error) => {
            console.warn('Failed to load prismarine-viewer:', error.message);
            console.warn('Bot view will be disabled, but bot will continue to work');
        });
    }
}