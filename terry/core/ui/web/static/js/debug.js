// Debug script para detectar bloqueos de clicks
console.log('🔍 DEBUG: Script cargado');

// Ejecutar después de que el DOM esté listo
window.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 DEBUG: DOM listo');

    setTimeout(() => {
        console.log('🔍 DEBUG: Iniciando diagnóstico...');

        // 1. Verificar TerryUI
        console.log('TerryUI existe?', typeof window.terryUI !== 'undefined');
        if (typeof window.terryUI !== 'undefined') {
            console.log('TerryUI:', window.terryUI);
        }

        // 2. Verificar modales
        const modals = document.querySelectorAll('.modal');
        console.log('Modales encontrados:', modals.length);
        modals.forEach((modal, i) => {
            const style = window.getComputedStyle(modal);
            const visible = style.display !== 'none';
            console.log(`Modal ${i} (${modal.id}):`, {
                display: style.display,
                visible: visible,
                zIndex: style.zIndex,
                position: style.position
            });

            if (visible) {
                console.warn('⚠️ MODAL VISIBLE:', modal.id);
                // Auto-fix: ocultar modal
                modal.style.display = 'none';
                console.log('✅ Modal ocultado:', modal.id);
            }
        });

        // 3. Buscar elementos con z-index muy alto
        const highZElements = [];
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            const zIndex = parseInt(style.zIndex);
            if (!isNaN(zIndex) && zIndex > 999) {
                highZElements.push({
                    element: el,
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    zIndex: zIndex,
                    display: style.display,
                    position: style.position,
                    pointerEvents: style.pointerEvents
                });
            }
        });

        if (highZElements.length > 0) {
            console.log('Elementos con z-index alto:', highZElements);
        }

        // 4. Buscar elementos que cubren toda la pantalla
        const fullScreenElements = [];
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();

            if (rect.width >= window.innerWidth * 0.9 &&
                rect.height >= window.innerHeight * 0.9 &&
                style.display !== 'none' &&
                (style.position === 'fixed' || style.position === 'absolute')) {

                fullScreenElements.push({
                    element: el,
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    zIndex: style.zIndex,
                    pointerEvents: style.pointerEvents,
                    position: style.position
                });
            }
        });

        if (fullScreenElements.length > 0) {
            console.warn('⚠️ Elementos cubriendo pantalla completa:', fullScreenElements);

            // AUTO-FIX: Ocultar elementos bloqueadores
            fullScreenElements.forEach((info, i) => {
                console.log(`Elemento bloqueador #${i}:`, {
                    tag: info.tag,
                    id: info.id,
                    className: info.className,
                    zIndex: info.zIndex,
                    pointerEvents: info.pointerEvents
                });

                // Si no es un contenedor principal, ocultarlo
                if (info.id !== 'app' && info.className.indexOf('container') === -1) {
                    console.log(`🔧 Ocultando elemento bloqueador: ${info.id || info.className}`);
                    info.element.style.display = 'none';
                    info.element.style.pointerEvents = 'none';
                }
            });
        }

        // 5. Test de múltiples clicks
        let clickCount = 0;
        document.addEventListener('click', (e) => {
            clickCount++;
            const el = document.elementFromPoint(e.clientX, e.clientY);
            console.log(`Click #${clickCount} detectado en:`, e.clientX, e.clientY);
            console.log('Elemento bajo el click:', {
                element: el,
                tag: el.tagName,
                id: el.id,
                className: el.className,
                clickable: el.onclick !== null || el.hasAttribute('onclick'),
                pointerEvents: window.getComputedStyle(el).pointerEvents,
                zIndex: window.getComputedStyle(el).zIndex
            });

            // Verificar si hay algo bloqueando después del click
            const blocker = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2);
            if (blocker && blocker.tagName !== 'BODY') {
                const style = window.getComputedStyle(blocker);
                if (style.pointerEvents === 'auto' &&
                    (style.position === 'fixed' || style.position === 'absolute') &&
                    parseInt(style.zIndex) > 100) {
                    console.warn('⚠️ Posible bloqueador en centro de pantalla:', {
                        tag: blocker.tagName,
                        id: blocker.id,
                        className: blocker.className
                    });
                }
            }
        });

        // 6. Auto-fix común: remover pointer-events: none de contenedores principales
        const mainContainer = document.querySelector('.container');
        if (mainContainer) {
            const style = window.getComputedStyle(mainContainer);
            if (style.pointerEvents === 'none') {
                console.warn('⚠️ Container principal tiene pointer-events: none');
                mainContainer.style.pointerEvents = 'auto';
                console.log('✅ Container arreglado');
            }
        }

        console.log('🔍 DEBUG: Diagnóstico completado');
        console.log('Haz click en cualquier parte para ver qué elemento se detecta');

    }, 1000);
});

// Exportar función para forzar arreglo manual
window.forceFixClicks = function() {
    console.log('🔧 Forzando arreglo de clicks...');

    // Remover todos los pointer-events: none
    let fixed = 0;
    document.querySelectorAll('*').forEach(el => {
        const style = window.getComputedStyle(el);
        if (style.pointerEvents === 'none') {
            el.style.pointerEvents = 'auto';
            fixed++;
        }
    });
    console.log(`✅ ${fixed} elementos con pointer-events arreglados`);

    // Ocultar todos los modales
    document.querySelectorAll('.modal').forEach(modal => {
        if (!modal.classList.contains('show')) {
            modal.style.display = 'none';
        }
    });
    console.log('✅ Modales ocultados');

    // Remover overlays invisibles
    document.querySelectorAll('[class*="overlay"]').forEach(overlay => {
        const style = window.getComputedStyle(overlay);
        if (style.display !== 'none') {
            overlay.style.display = 'none';
            console.log('✅ Overlay removido:', overlay.className);
        }
    });

    console.log('✅ Arreglo completado. Intenta hacer click ahora.');
};

console.log('💡 Tip: Si los clicks no funcionan, ejecuta en consola: forceFixClicks()');
