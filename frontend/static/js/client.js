const srcIconPasswordShow = '/static/img/icon-password-show.svg';
const srcIconPasswordHide = '/static/img/icon-password-hide.svg';
const hrefIconPageBeginning = '/static/img/icon-client-';
const hrefIconPageEnding = '.svg';

const indicationNeutral = 'neutral';
const indicationSuccess = 'success';
const indicationWarning = 'warning';

const recommendedMinLength = 8;
const recommendedMinDifferentSymbols = 5;
const criticalLeakThreshold = 5;

const passwordCheckDelay = 240;

const rangeApiBaseUri = '/range/';

function setPageIndication(indication) {
    document.body.className = `page-${indication}`;
    document.getElementById('favicon').href;
    favicon.href = `${hrefIconPageBeginning}${indication}${hrefIconPageEnding}`;
}

function togglePasswordVisibility() {
    const input = document.getElementById('input-password');
    const visibilityToggle = document.getElementById(
        'password-visibility-toggle',
    );
    if (input.type === 'password') {
        input.type = 'text';
        visibilityToggle.src = srcIconPasswordHide;
    } else {
        input.type = 'password';
        visibilityToggle.src = srcIconPasswordShow;
    }
}

function getPasswordInfoBlock() {
    return document.getElementById('block-password-info');
}

function getCurrentPassword() {
    return document.getElementById('input-password').value;
}

function isTooShort(password) {
    return password.length < recommendedMinLength;
}

function isDiverse(password) {
    return recommendedMinDifferentSymbols <= new Set(password).size;
}

function hasOnlyDigits(password) {
    return /^\d+$/.test(password);
}

function hasOnlyLowercaseLetters(password) {
    return /^[a-z]+$/.test(password);
}

function hasOnlyUppercaseLetters(password) {
    return /^[A-Z]+$/.test(password);
}

function showPasswordInfo(password, leakOccasionNumber) {
    let content = '';
    const isNotLeaked = leakOccasionNumber === 0;
    if (leakOccasionNumber === null) {
        content += '<p>Ошибка: Не удалось проверить пароль на утечки</p>';
    } else {
        if (leakOccasionNumber === 0) {
            content += '<p class="text-success">Утечек не обнаружено</p>';
        } else if (leakOccasionNumber < criticalLeakThreshold) {
            content += '<p>Обнаружено несколько утечек</p>';
        } else {
            content += '<p>Обнаружено множество утечек</p>';
        }
    }
    let isWeak = false;
    if (isTooShort(password)) {
        isWeak = true;
        content += `<p>Пароль должен иметь длину не менее ${recommendedMinLength} символов</p>`;
    } else {
        if (!isDiverse(password)) {
            isWeak = true;
            content += `<p>Пароль должен включать не менее ${recommendedMinDifferentSymbols} различных символов</p>`;
        } else {
            if (hasOnlyDigits(password)) {
                isWeak = true;
                content += `<p>Пароль не должен состоять только из цифр</p>`;
            }
            if (hasOnlyLowercaseLetters(password)) {
                isWeak = true;
                content += `<p>Пароль не должен состоять только из строчных латинских букв</p>`;
            }
            if (hasOnlyUppercaseLetters(password)) {
                isWeak = true;
                content += `<p>Пароль не должен состоять только из прописных латинских букв</p>`;
            }
        }
    }
    getPasswordInfoBlock().innerHTML = content;
    getPasswordInfoBlock().removeAttribute('hidden');
    setPageIndication(
        !isNotLeaked || isWeak ? indicationWarning : indicationSuccess,
    );
}

function countLeakOccasions(leakRecords, hashSuffix) {
    const lines = leakRecords.split(/\r?\n/);
    for (const line of lines) {
        const [suffix, occasionCount] = line.split(':');
        if (suffix === hashSuffix) {
            return parseInt(occasionCount, 10) || null;
        }
    }
    return 0;
}

async function checkPasswordIfNotUpdated(password) {
    if (password !== getCurrentPassword()) {
        return;
    }
    const passwordHash = CryptoJS.SHA1(password)
        .toString(CryptoJS.enc.Hex)
        .toUpperCase();
    const hashPrefix = passwordHash.slice(0, 5);
    const hashSuffix = passwordHash.slice(5);
    await $.ajax({
        url: rangeApiBaseUri + hashPrefix,
        method: 'GET',
        success: function (data) {
            showPasswordInfo(password, countLeakOccasions(data, hashSuffix));
        },
        error: function () {
            showPasswordInfo(password, null);
        },
    });
}

function handlePasswordInput() {
    const currentPassword = getCurrentPassword();
    if (currentPassword === '') {
        setPageIndication(indicationNeutral);
        getPasswordInfoBlock().innerHTML = '';
        getPasswordInfoBlock().setAttribute('hidden', 'true');
        return;
    }
    setTimeout(async () => {
        await checkPasswordIfNotUpdated(currentPassword);
    }, passwordCheckDelay);
}
