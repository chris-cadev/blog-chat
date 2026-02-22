declare module 'htmx.org' {
  const htmx: {
    on: (event: string, handler: (evt: Event) => void) => void;
    off: (event: string, handler: (evt: Event) => void) => void;
    trigger: (elt: HTMLElement, event: string, detail?: object) => void;
    ajax: (verb: string, path: string, options: object) => void;
    process: (elt: HTMLElement) => void;
    find: (selector: string, root?: HTMLElement) => HTMLElement | null;
    findAll: (selector: string, root?: HTMLElement) => HTMLElement[];
    findAllToArray: (selector: string, root?: HTMLElement) => HTMLElement[];
    remove: (elt: HTMLElement) => void;
    addClass: (elt: HTMLElement, classname: string) => void;
    removeClass: (elt: HTMLElement, classname: string) => void;
    toggleClass: (elt: HTMLElement, classname: string) => void;
    hasClass: (elt: HTMLElement, classname: string) => boolean;
    swap: (outer: HTMLElement, inner: string, swapSpec: object) => void;
    defineExtension: (name: string, ext: object) => void;
    removeExtension: (name: string) => void;
    extend: (extension: object) => object;
    config: {
      defaultSwapStyle: string;
      defaultSwapDelay: number;
      defaultSettleDelay: number;
      includeIndicatorStyles: boolean;
      indicatorClass: string;
      requestClass: string;
      settlingClass: string;
      swapClass: string;
      disabledIndicators: string;
      enabledIndicators: string;
      allowScriptTags: boolean;
      inlineScriptNonce: string;
      inlineStyleNonce: string;
      attributesToSettle: string[];
      multiScriptTargets: boolean;
      defaultFocusScroll: boolean;
      cacheBuster: boolean;
      viewTransition: boolean;
      timeout: number;
      maxRequestTime: number;
    };
  };
  export default htmx;
}

interface Window {
  htmx: any;
}
