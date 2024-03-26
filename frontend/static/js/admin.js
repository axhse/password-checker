const pageAutoUpdateInterval = 60000;

const apiBaseUri = '/admin/';

function redirectToLoginPage() {
    window.location.href = apiBaseUri + 'login';
}

function updateRevisionButtons(revisionStatus) {
    const buttonRevisionStart = document.getElementById(
        'button-revision-start',
    );
    const buttonRevisionCancel = document.getElementById(
        'button-revision-cancel',
    );
    if (
        revisionStatus === 'new' ||
        revisionStatus === 'completed' ||
        revisionStatus === 'failed' ||
        revisionStatus === 'cancelled'
    ) {
        buttonRevisionStart.hidden = false;
    } else {
        buttonRevisionStart.hidden = true;
    }
    buttonRevisionCancel.hidden = revisionStatus !== 'preparation';
}

function showRevisionInfo(data) {
    let content = '';
    if (data == null) {
        content +=
            '<p class="revision-no-info">Не получилось загрузить информацию</p>';
    } else {
        updateRevisionButtons(data.status);
        let statusName = '?';
        switch (data.status) {
            case 'new':
                statusName = 'Пока что не было обновлений';
                break;
            case 'preparation':
                statusName = 'Подготовка данных';
                break;
            case 'transition':
                statusName = 'Переключение на новые данные';
                break;
            case 'purge':
                statusName = 'Очистка старых данных';
                break;
            case 'cancellation':
                statusName = 'Выполняется отмена обновления';
                break;
            case 'completed':
                statusName = 'Обновление успешно завершено';
                break;
            case 'failed':
                statusName = 'Обновление завершилось с ошибкой';
                break;
            case 'cancelled':
                statusName = 'Обновление было отменено';
                break;
        }
        content += `<p><span class="revision-prop">Статус</span>&nbsp;&nbsp;${statusName}</p>`;
        if (data.progress !== null && data.progress !== undefined) {
            content += `<p class="revision-progress"><span class="revision-prop">Прогресс подготовки данных</span>&nbsp;&nbsp;${data.progress}%</p>`;
        }
        if (data.error_message !== null && data.error_message !== undefined) {
            content += `<p class="revision-error-message"><span class="revision-prop">Сообщение ошибки</span>&nbsp;&nbsp;${data.error_message}</p>`;
        }
        if (data.start_ts !== null && data.start_ts !== undefined) {
            const start_datetime = new Date(
                data.start_ts * 1000,
            ).toLocaleString('ru-RU');
            content += `<p><span class="revision-prop">Время начала обновления</span>&nbsp;&nbsp;${start_datetime}</p>`;
        }
        if (data.end_ts !== null && data.end_ts !== undefined) {
            const end_datetime = new Date(data.end_ts * 1000).toLocaleString(
                'ru-RU',
            );
            content += `<p><span class="revision-prop">Время завершения обновления</span>&nbsp;&nbsp;${end_datetime}</p>`;
        }
    }
    const revisionInfoBlock = document.getElementById('block-revision-info');
    revisionInfoBlock.innerHTML = content;
    revisionInfoBlock.removeAttribute('hidden');
}

async function updateRevisionInfo() {
    await $.ajax({
        url: apiBaseUri + 'revision',
        method: 'GET',
        success: function (data) {
            showRevisionInfo(data);
        },
        error: function (response) {
            if (response.status === 401) {
                redirectToLoginPage();
            }
            showRevisionInfo(null);
        },
    });
}

async function requestUpdate() {
    await $.ajax({
        url: apiBaseUri + 'revision/start',
        method: 'POST',
        error: function (response) {
            if (response.status === 401) {
                redirectToLoginPage();
            }
        },
    });
    await updateRevisionInfo();
}

async function requestUpdateCancellation() {
    await $.ajax({
        url: apiBaseUri + 'revision/cancel',
        method: 'POST',
        error: function (response) {
            if (response.status === 401) {
                redirectToLoginPage();
            }
        },
    });
    await updateRevisionInfo();
}

async function initializePage() {
    await updateRevisionInfo();
    document.getElementById('div-revision').hidden = false;
    setInterval(async () => {
        await updateRevisionInfo();
    }, pageAutoUpdateInterval);
}
