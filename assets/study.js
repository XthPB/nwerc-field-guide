(() => {
  function revealAnchor() {
    const target = document.getElementById(location.hash.slice(1));
    if (target && target.matches("details.unit")) target.open = true;
  }
  revealAnchor();
  window.addEventListener("hashchange", revealAnchor);
  for (const figure of document.querySelectorAll("[data-trace]")) {
    const frames = Array.from(figure.querySelectorAll("ol > li"));
    const controls = document.createElement("div");
    const indicator = document.createElement("output");
    indicator.setAttribute("aria-live", "polite");
    controls.className = "step-controls";
    function button(caption) {
      const element = document.createElement("button");
      element.type = "button";
      element.textContent = caption;
      return element;
    }
    const back = button("Previous"),
      next = button("Next"),
      play = button("Play");
    controls.append(back, play, indicator, next);
    figure.append(controls);
    let index = 0;
    let timer = null;
    function stop() {
      clearInterval(timer);
      timer = null;
      play.textContent = "Play";
      play.setAttribute("aria-pressed", "false");
    }
    function draw() {
      frames.forEach((frame, i) => {
        frame.hidden = i !== index;
      });
      indicator.textContent = "Step " + (index + 1) + " of " + frames.length;
      back.disabled = index === 0;
      next.disabled = index === frames.length - 1;
    }
    back.addEventListener("click", () => {
      stop();
      if (index > 0) index--;
      draw();
    });
    next.addEventListener("click", () => {
      stop();
      if (index + 1 < frames.length) index++;
      draw();
    });
    play.addEventListener("click", () => {
      if (timer !== null) {
        stop();
        return;
      }
      if (index === frames.length - 1) {
        index = 0;
        draw();
      }
      play.textContent = "Pause";
      play.setAttribute("aria-pressed", "true");
      timer = setInterval(() => {
        index++;
        draw();
        if (index === frames.length - 1) stop();
      }, 2600);
    });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stop();
    });
    stop();
    draw();
  }
})();
