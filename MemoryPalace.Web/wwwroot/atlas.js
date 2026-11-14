window.memoryPalace = {
    ready: () => { document.body.dataset.atlasReady = "true"; },
    size: element => {
        const rect = element.getBoundingClientRect();
        return [rect.width, rect.height];
    },
    capturePointer: (element, pointerId) => element.setPointerCapture(pointerId),
    openDialog: dialog => dialog.showModal(),
    download: (name, content) => {
        const url = URL.createObjectURL(new Blob([content], { type: 'application/json' }));
        const link = document.createElement('a');
        link.href = url;
        link.download = name;
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
};
