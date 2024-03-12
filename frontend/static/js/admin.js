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
        content += '<p class="revision-no-info">Error: Unable to get information</p>';
    } else {
        updateRevisionButtons(data.status);
        let statusText = '?';
        switch (data.status) {
            case 'new':
                statusText = 'There were no updated since app launch';
                break;
            case 'preparation':
                statusText = 'New data is being prepared';
                break;
            case 'transition':
                statusText = 'Switching to new data';
                break;
            case 'purge':
                statusText = 'Cleaning up old data';
                break;
            case 'cancellation':
                statusText = 'The update is being canceled';
                break;
            case 'completed':
                statusText = 'The update has been completed successfully';
                break;
            case 'failed':
                statusText = 'The update failed with an error';
                break;
            case 'cancelled':
                statusText = 'The update has been canceled';
                break;
        }
        content += `<p><span class="revision-prop">Status</span>&nbsp;&nbsp;${statusText}</p>`;
        if (data.progress !== null && data.progress !== undefined) {
            content += `<p class="revision-progress"><span class="revision-prop">Data preparation progress</span>&nbsp;&nbsp;${data.progress}%</p>`;
        }
        if (data.error_message !== null && data.error_message !== undefined) {
            content += `<p class="revision-error-message"><span class="revision-prop">Error message</span>&nbsp;&nbsp;${data.error_message}</p>`;
        }
        if (data.start_ts !== null && data.start_ts !== undefined) {
            const start_datetime = new Date(
                data.start_ts * 1000,
            ).toLocaleString('ru-RU');
            content += `<p><span class="revision-prop">Start time</span>&nbsp;&nbsp;${start_datetime}</p>`;
        }
        if (data.end_ts !== null && data.end_ts !== undefined) {
            const end_datetime = new Date(data.end_ts * 1000).toLocaleString(
                'ru-RU',
            );
            content += `<p><span class="revision-prop">End time</span>&nbsp;&nbsp;${end_datetime}</p>`;
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
