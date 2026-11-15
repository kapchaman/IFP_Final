window.memoryPalace = {
    ready: () => { document.body.dataset.atlasReady = "true"; },
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

(() => {
    const graphs = new WeakMap();
    const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

    memoryPalace.initializeGraph = (canvas, receiver) => {
        graphs.get(canvas)?.dispose();
        const world = canvas.querySelector('.graph-world');
        let zoom = 1, panX = 0, panY = 0;
        let gesture = null, frame = null, suppressClick = false, clickTimer = null;

        function renderCamera() {
            world.style.transform = `translate(${panX}px,${panY}px) scale(${zoom})`;
        }

        function renderGesture() {
            frame = null;
            if (!gesture?.moved) return;
            const { node, dx, dy } = gesture;
            if (node) {
                gesture.x = clamp(gesture.startX + dx * 100 / gesture.width / zoom, 2, 98);
                gesture.y = clamp(gesture.startY + dy * 100 / gesture.height / zoom, 2, 98);
                node.style.left = `${gesture.x}%`;
                node.style.top = `${gesture.y}%`;
                for (const edge of gesture.edges) {
                    const source = edge.dataset.source === node.dataset.conceptId;
                    edge.setAttribute(source ? 'x1' : 'x2', gesture.x * 8);
                    edge.setAttribute(source ? 'y1' : 'y2', gesture.y * 4.6);
                }
            } else {
                panX = gesture.startX + dx;
                panY = gesture.startY + dy;
                renderCamera();
            }
        }

        function move(event) {
            if (!gesture || event.pointerId !== gesture.pointerId) return;
            gesture.dx = event.clientX - gesture.clientX;
            gesture.dy = event.clientY - gesture.clientY;
            if (Math.hypot(gesture.dx, gesture.dy) >= 4) gesture.moved = true;
            if (gesture.moved && frame === null) frame = requestAnimationFrame(renderGesture);
        }

        function finish(event, commit = true) {
            if (!gesture || event.pointerId !== gesture.pointerId) return;
            if (frame !== null) cancelAnimationFrame(frame);
            renderGesture();
            const completed = gesture;
            gesture = null;
            canvas.removeEventListener('pointermove', move);
            canvas.removeEventListener('pointerup', finish);
            canvas.removeEventListener('pointercancel', cancel);
            canvas.removeEventListener('lostpointercapture', cancel);
            if (completed.capture.hasPointerCapture(completed.pointerId)) completed.capture.releasePointerCapture(completed.pointerId);
            suppressClick = completed.moved;
            clearTimeout(clickTimer);
            clickTimer = setTimeout(() => { suppressClick = false; }, 0);
            if (commit && completed.node && completed.moved && completed.node.isConnected) {
                receiver.invokeMethodAsync('CommitNodePosition', completed.node.dataset.conceptId, completed.x, completed.y)
                    .catch(error => console.error('Could not save the graph position.', error));
            }
        }

        function cancel(event) {
            if (!gesture || event.pointerId !== gesture.pointerId) return;
            // Keep the last displayed position, but end capture even if touch input is cancelled.
            finish(event);
            suppressClick = false;
        }

        function start(event) {
            if (gesture || event.button !== 0 || event.isPrimary === false || event.target.closest('.graph-zoom')) return;
            const node = event.target.closest('.graph-node');
            const size = canvas.getBoundingClientRect();
            const capture = node || canvas;
            gesture = {
                pointerId: event.pointerId, capture, node,
                clientX: event.clientX, clientY: event.clientY, dx: 0, dy: 0, moved: false,
                startX: node ? parseFloat(node.style.left) : panX,
                startY: node ? parseFloat(node.style.top) : panY,
                width: Math.max(size.width, 1), height: Math.max(size.height, 1),
                edges: node ? [...world.querySelectorAll('line')].filter(edge =>
                    edge.dataset.source === node.dataset.conceptId || edge.dataset.target === node.dataset.conceptId) : []
            };
            // Capture on the pressed button so a normal click still selects that concept.
            capture.setPointerCapture(event.pointerId);
            canvas.addEventListener('pointermove', move);
            canvas.addEventListener('pointerup', finish);
            canvas.addEventListener('pointercancel', cancel);
            canvas.addEventListener('lostpointercapture', cancel);
        }

        function setZoom(value) {
            if (gesture) return;
            zoom = clamp(value, 0.5, 2.5);
            renderCamera();
        }

        function wheel(event) {
            if (!event.deltaY) return;
            event.preventDefault();
            setZoom(zoom * (event.deltaY < 0 ? 1.1 : 1 / 1.1));
        }

        function click(event) {
            if (suppressClick && event.detail > 0) {
                suppressClick = false;
                event.preventDefault();
                event.stopImmediatePropagation();
                return;
            }
            const action = event.target.closest('[data-graph-action]')?.dataset.graphAction;
            if (action === 'zoom-in') setZoom(zoom * 1.2);
            if (action === 'zoom-out') setZoom(zoom / 1.2);
            if (action === 'reset' && !gesture) {
                zoom = 1;
                panX = panY = 0;
                renderCamera();
            }
        }

        canvas.addEventListener('pointerdown', start);
        canvas.addEventListener('wheel', wheel, { passive: false });
        canvas.addEventListener('click', click, true);
        renderCamera();
        graphs.set(canvas, {
            dispose() {
                if (gesture) finish({ pointerId: gesture.pointerId }, false);
                if (frame !== null) cancelAnimationFrame(frame);
                clearTimeout(clickTimer);
                canvas.removeEventListener('pointerdown', start);
                canvas.removeEventListener('wheel', wheel);
                canvas.removeEventListener('click', click, true);
                graphs.delete(canvas);
            }
        });
    };

    memoryPalace.disposeGraph = canvas => graphs.get(canvas)?.dispose();
})();
