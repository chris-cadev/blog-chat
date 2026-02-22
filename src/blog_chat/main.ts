import "./styles/main.css";

const htmx = await import("htmx.org");
window.htmx = htmx.default;

await import("htmx.org/dist/ext/ws");
