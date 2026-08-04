function isIframeLoaded(iframe: HTMLIFrameElement): boolean {
  try {
    return iframe.contentDocument?.readyState === "complete";
  } catch {
    return false;
  }
}

export function initIframeLoader() {
  document
    .querySelectorAll<HTMLIFrameElement>(".markdown iframe")
    .forEach((iframe) => {
      if (iframe.closest(".iframe-loader")) return;

      const wrapper = document.createElement("div");
      wrapper.className = "iframe-loader";

      if (getComputedStyle(iframe).position === "absolute") {
        wrapper.classList.add("iframe-loader--absolute");
      }

      const spinner = document.createElement("span");
      spinner.className = "iframe-loader__spinner";
      spinner.setAttribute("aria-hidden", "true");

      const loading = document.createElement("span");
      loading.className = "loading loading-spinner loading-lg";
      spinner.appendChild(loading);

      iframe.parentNode?.insertBefore(wrapper, iframe);
      wrapper.appendChild(iframe);
      wrapper.appendChild(spinner);

      const finish = () => wrapper.classList.add("iframe-loader--loaded");
      if (isIframeLoaded(iframe)) {
        finish();
      } else {
        iframe.addEventListener("load", finish);
        iframe.addEventListener("error", finish);
      }
    });
}
