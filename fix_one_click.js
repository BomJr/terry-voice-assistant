// Script para diagnosticar el problema de "solo un click"
console.log('=== DIAGNÓSTICO DE UN SOLO CLICK ===');

// 1. Ver el elemento que cubre la pantalla
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
            position: style.position,
            display: style.display,
            top: style.top,
            left: style.left
        });
    }
});

console.log('Elementos cubriendo pantalla:', fullScreenElements);

// 2. Expandir el primero para ver todos sus detalles
if (fullScreenElements.length > 0) {
    const blocker = fullScreenElements[0];
    console.log('🚨 ELEMENTO BLOQUEADOR:', blocker);
    console.log('HTML del elemento:', blocker.element.outerHTML.substring(0, 500));

    // ARREGLARLO
    console.log('Intentando arreglar...');
    blocker.element.style.display = 'none';
    console.log('✅ Elemento ocultado');
}

// 3. Listener para múltiples clicks
let clickCount = 0;
document.addEventListener('click', (e) => {
    clickCount++;
    console.log(`Click #${clickCount} detectado en:`, {
        x: e.clientX,
        y: e.clientY,
        elemento: e.target.tagName,
        id: e.target.id,
        className: e.target.className
    });

    // Ver qué hay bajo el cursor
    const el = document.elementFromPoint(e.clientX, e.clientY);
    console.log('Elemento bajo cursor:', {
        tag: el.tagName,
        id: el.id,
        className: el.className,
        zIndex: window.getComputedStyle(el).zIndex,
        pointerEvents: window.getComputedStyle(el).pointerEvents
    });
});

console.log('Haz varios clicks y observa...');
