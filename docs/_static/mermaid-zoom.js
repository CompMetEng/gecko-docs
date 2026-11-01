/* Zoom of the flowcharts.
 *
 * The d3 zoom of sphinxcontrib-mermaid takes every mouse wheel event over a
 * diagram, so a page with a tall diagram cannot be scrolled with the pointer
 * on it. In the page, the wheel zooms only with Ctrl (or Cmd) held; in the
 * full-screen view, the wheel always zooms. Dragging pans in both.
 */
(function () {
  "use strict";

  function guard(event) {
    if (event.ctrlKey || event.metaKey) return;
    var target = event.target;
    if (!target || !target.closest) return;
    var container = target.closest(".mermaid-container");
    if (!container || container.classList.contains("mermaid-container-fullscreen")) return;
    if (target.closest(".mermaid-fullscreen-modal")) return;
    event.stopPropagation();
  }

  document.addEventListener("wheel", guard, { capture: true, passive: true });
})();
