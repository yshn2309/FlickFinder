const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

window.telegramUser = tg.initDataUnsafe?.user || null;