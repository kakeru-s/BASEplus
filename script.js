// 公開時に公式LINE URLを設定すると、ページ内の全LINEボタンへ反映されます。
const OFFICIAL_LINE_URL = "https://lin.ee/PNj9ilg";

document.querySelectorAll(".js-line-link").forEach((link) => {
  if (OFFICIAL_LINE_URL) {
    link.href = OFFICIAL_LINE_URL;
    link.target = "_blank";
    link.rel = "noopener";
  }
});

const sendGaEvent = (eventName, params = {}) => {
  if (typeof window.gtag !== "function") return;
  window.gtag("event", eventName, {
    transport_type: "beacon",
    ...params,
  });
};

document.querySelectorAll("[data-ga-event]").forEach((element) => {
  element.addEventListener("click", () => {
    const eventName = element.dataset.gaEvent;
    const eventParams = {
      click_location: element.dataset.gaLocation || "unknown",
      event_label: element.dataset.gaLabel || element.textContent.trim(),
      link_url: element.href || "",
      link_text: element.textContent.trim().replace(/\s+/g, " "),
    };

    sendGaEvent(eventName, eventParams);

    if (element.dataset.gaTrial === "true") {
      sendGaEvent("trial_lesson_click", eventParams);
    }
  });
});

const menuButton = document.querySelector(".menu-button");
const nav = document.querySelector(".nav");
menuButton.addEventListener("click", () => {
  const open = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!open));
  nav.classList.toggle("open", !open);
});
nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  nav.classList.remove("open");
  menuButton.setAttribute("aria-expanded", "false");
}));

if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));
}
