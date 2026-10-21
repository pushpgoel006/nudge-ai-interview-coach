"use client";

import { useLayoutEffect, type ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

/**
 * Scroll choreography for the landing page. The sections are server-rendered
 * and static; this component only layers motion on top. With reduced motion
 * (or if anything here fails) the page stays a plain, fully readable document.
 */
export function Motion({ children }: { children: ReactNode }) {
  useLayoutEffect(() => {
    const loader = document.getElementById("loader");
    const finishLoading = () => {
      if (loader) loader.style.display = "none";
      document.body.classList.remove("is-loading");
    };

    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      finishLoading();
      return;
    }

    gsap.registerPlugin(ScrollTrigger);
    document.body.classList.add("is-loading");

    const q = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document) =>
      [...root.querySelectorAll<T>(sel)];

    /* ---------- smooth scroll ---------- */
    const lenis = new Lenis({ lerp: 0.1 });
    lenis.on("scroll", ScrollTrigger.update);
    const tick = (t: number) => lenis.raf(t * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    lenis.stop();

    const onAnchorClick = (e: Event) => {
      const a = e.currentTarget as HTMLAnchorElement;
      const id = a.getAttribute("href") ?? "";
      const target = id.length > 1 ? document.querySelector<HTMLElement>(id) : null;
      if (target) {
        e.preventDefault();
        lenis.scrollTo(target);
      }
    };
    const anchors = q<HTMLAnchorElement>('a[href^="#"]');
    anchors.forEach((a) => a.addEventListener("click", onAnchorClick));

    const ctx = gsap.context(() => {
      /* ---------- loader -> hero ---------- */
      const heroChars = q(".hero__title .ch");
      const counter = { v: 0 };
      const countEl = document.getElementById("count");
      const segs = q("#loaderMeter i");

      gsap.set(heroChars, { yPercent: 110 });
      gsap.set(".hero__shape", { scale: 0.6, opacity: 0 });
      gsap.set(".hero__row span, .hero__cap, .bar", { opacity: 0 });

      gsap
        .timeline({ defaults: { ease: "expo.out" } })
        .to(counter, {
          v: 100,
          duration: 2,
          ease: "power2.inOut",
          onUpdate: () => {
            if (countEl) countEl.textContent = String(Math.round(counter.v)).padStart(3, "0");
            segs.forEach((s, i) => s.classList.toggle("on", counter.v >= (i + 1) * 10 - 0.01));
          },
        })
        .to(loader, { yPercent: -100, duration: 1.1, ease: "expo.inOut" })
        .add(() => {
          document.body.classList.remove("is-loading");
          lenis.start();
        }, "-=0.5")
        .to(".hero__shape", { scale: 1, opacity: 1, duration: 1.3, stagger: 0.12 }, "-=0.7")
        .to(heroChars, { yPercent: 0, duration: 1, stagger: 0.025 }, "<0.1")
        .to(".hero__row span, .hero__cap, .bar", { opacity: 1, duration: 0.8, stagger: 0.08 }, "-=0.6")
        .add(() => {
          if (loader) loader.style.display = "none";
        });

      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: no-preference)", () => {
        /* hero: pinned, type parts */
        gsap
          .timeline({
            scrollTrigger: { trigger: ".hero", start: "top top", end: "+=110%", scrub: 0.8, pin: true, anticipatePin: 1 },
          })
          .to(".hero__title", { yPercent: -140, ease: "none" }, 0)
          .to("#heroL", { xPercent: -45, ease: "none" }, 0)
          .to("#heroR", { xPercent: 45, ease: "none" }, 0)
          .to(".hero__shape--a", { rotate: 40, xPercent: -12, ease: "none" }, 0)
          .to(".hero__shape--b", { yPercent: 40, ease: "none" }, 0)
          .to(".hero__cap", { opacity: 0, ease: "none" }, 0);

        /* word-by-word reveals */
        q(".reveal").forEach((el) => {
          const words = q(".w", el);
          if (el.closest(".finale__t")) {
            gsap.from(words, {
              yPercent: 80, opacity: 0, duration: 1, stagger: 0.12, ease: "expo.out",
              scrollTrigger: { trigger: el, start: "top 85%" },
            });
            return;
          }
          gsap.fromTo(words, { opacity: 0.12 }, {
            opacity: 1, ease: "none", stagger: 0.12,
            scrollTrigger: { trigger: el, start: "top 82%", end: "bottom 48%", scrub: true },
          });
        });

        /* stages: figure scales up, title rises */
        q(".stage").forEach((stage) => {
          const img = stage.querySelector(".stage__img");
          if (img) {
            gsap.fromTo(img, { scale: 0.45, yPercent: 18 }, {
              scale: 1.15, yPercent: -4, ease: "none",
              scrollTrigger: { trigger: stage, start: "top bottom", end: "bottom top", scrub: true },
            });
          }
          gsap.from(q(".ch", stage), {
            yPercent: 105, duration: 1, stagger: 0.04, ease: "expo.out",
            scrollTrigger: { trigger: stage, start: "top 40%" },
          });
        });

        /* body blocks fade up */
        q(".steps li, .ui").forEach((el) => {
          gsap.from(el, {
            y: 36, opacity: 0, duration: 0.9, ease: "expo.out",
            scrollTrigger: { trigger: el, start: "top 90%" },
          });
        });

        /* ---- product boxes: numbers count up and parts play in once, when seen ---- */
        const count = (el: HTMLElement, dur = 1.6, ease = "power3.out") => {
          const end = parseFloat(el.dataset.count ?? "0");
          const dec = Number(el.dataset.dec ?? 0);
          const o = { v: 0 };
          el.textContent = (0).toFixed(dec);
          return gsap.to(o, { v: end, duration: dur, ease, onUpdate: () => { el.textContent = o.v.toFixed(dec); } });
        };
        const onView = (box: Element) =>
          gsap.timeline({
            defaults: { ease: "expo.out" },
            scrollTrigger: { trigger: box, start: "top 80%", once: true },
          });

        const chat = document.querySelector<HTMLElement>(".ui--chat");
        if (chat) {
          const tl = onView(chat);
          tl.from(chat.querySelector(".msg--you"), { opacity: 0, y: 14, duration: 0.6 }).addLabel("trace", "+=0.15");
          q(".trace li", chat).forEach((li, i) => {
            tl.from(li, { opacity: 0.15, y: 8, duration: 0.5 }, "trace+=" + i * 0.45);
            const n = li.querySelector<HTMLElement>("[data-count]");
            if (n) tl.add(count(n, 0.7, "power2.out"), "trace+=" + i * 0.45);
          });
          tl.from(chat.querySelector(".msg--ai"), { opacity: 0, y: 14, duration: 0.7 }, ">-0.1")
            .from(q(".chips li", chat), { opacity: 0, y: 8, duration: 0.5, stagger: 0.12 }, ">-0.2");
        }

        const resume = document.querySelector<HTMLElement>(".ui--resume");
        if (resume) {
          onView(resume)
            .add(count(resume.querySelector<HTMLElement>(".fit strong")!, 1.8))
            .from(q(".fit span", resume), { opacity: 0, duration: 0.6 }, 0.2)
            .from(q(".verdicts li", resume), { opacity: 0, x: -16, duration: 0.6, stagger: 0.3 }, 0.7);
        }

        const theory = document.querySelector<HTMLElement>(".ui--theory");
        if (theory) {
          const on = q(".meter i", theory).filter((i) => i.classList.contains("on"));
          gsap.set(on, { backgroundColor: "rgba(17,17,17,0)" });
          onView(theory)
            .from(q(".theory__q > *", theory), { opacity: 0, y: 12, duration: 0.6, stagger: 0.12 })
            .addLabel("score", ">-0.1")
            .add(count(theory.querySelector<HTMLElement>(".score strong")!, 1.8, "power2.out"), "score")
            .to(on, { backgroundColor: "#111", duration: 0.1, ease: "none", stagger: 1.8 / 7 }, "score")
            .from(q(".theory__eval > :not(.score):not(.meter)", theory), { opacity: 0, y: 10, duration: 0.6, stagger: 0.18 }, "score+=1");
        }

        const dsa = document.querySelector<HTMLElement>(".ui--dsa");
        if (dsa) {
          onView(dsa)
            .from(q(".dsa__t, .code", dsa), { opacity: 0, y: 12, duration: 0.6, stagger: 0.12 })
            .add(count(dsa.querySelector<HTMLElement>(".score strong")!, 1.4), ">-0.1")
            .from(q(".dsa__r p", dsa), { opacity: 0, x: -12, duration: 0.6, stagger: 0.2 }, "<0.4");
        }

        const dash = document.querySelector<HTMLElement>(".ui--dash");
        const ring = document.getElementById("ringFg");
        const num = document.getElementById("ringNum");
        if (dash && ring && num) {
          const end = parseFloat(num.dataset.count ?? "0");
          const o = { v: 0 };
          ring.style.strokeDashoffset = "263.9";
          num.textContent = "0";
          const tl = onView(dash);
          tl.to(o, {
            v: end, duration: 2, ease: "power3.out",
            onUpdate: () => {
              num.textContent = String(Math.round(o.v));
              ring.style.strokeDashoffset = String(263.9 * (1 - o.v / 100));
            },
          })
            .fromTo(dash.querySelector(".trend__line"), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.6, ease: "power2.out" }, 0.5)
            .from(q(".trend circle", dash), { opacity: 0, scale: 0, transformOrigin: "50% 50%", duration: 0.4, stagger: 0.25 }, 0.6);
          q(".bars li", dash).forEach((li, i) => {
            const bar = li.querySelector<HTMLElement>("i")!;
            const target = bar.style.getPropertyValue("--w");
            tl.fromTo(bar, { "--w": "0%" }, { "--w": target, duration: 1.2, ease: "power3.out" }, 0.9 + i * 0.2);
            tl.add(count(li.querySelector<HTMLElement>("b")!, 1.2), 0.9 + i * 0.2);
          });
        }
      });

      /* gallery: pinned horizontal scroll on large screens only */
      mm.add("(min-width: 901px) and (prefers-reduced-motion: no-preference)", () => {
        const track = document.getElementById("galleryTrack");
        const section = document.querySelector(".gallery");
        if (!track || !section) return;
        const dist = () => Math.max(0, track.scrollWidth - window.innerWidth);
        gsap.to(track, {
          x: () => -dist(), ease: "none",
          scrollTrigger: {
            trigger: section, start: "top top", end: () => "+=" + dist(), scrub: 0.6, pin: true,
            anticipatePin: 1, invalidateOnRefresh: true,
          },
        });
      });

      /* ---------- header: act label + backdrop colour ---------- */
      const bar = document.getElementById("bar");
      const barAct = document.getElementById("barAct");
      q("[data-act]").forEach((sec) => {
        ScrollTrigger.create({
          trigger: sec, start: "top 50%", end: "bottom 50%",
          onToggle: (self) => { if (self.isActive && barAct) barAct.textContent = sec.dataset.act ?? ""; },
        });
      });
      const activeDark = new Set<Element>();
      [".stage--black", ".finale", ".foot"].forEach((sel) =>
        q(sel).forEach((z) =>
          ScrollTrigger.create({
            trigger: z, start: "top 28px", end: "bottom 28px",
            onToggle: (self) => {
              if (self.isActive) activeDark.add(z); else activeDark.delete(z);
              bar?.classList.toggle("on-dark", activeDark.size > 0);
            },
          }),
        ),
      );
      ([
        [".hero", "#f3f1ea"], [".manifesto", "#f3f1ea"], [".stage--yellow", "#f9bb5f"], [".stage--rose", "#de8fc6"],
        [".stage--black", "#121212"], [".act__body", "#f3f1ea"], [".gallery", "#f3f1ea"], [".finale", "#121212"], [".foot", "#121212"],
      ] as const).forEach(([sel, col]) =>
        q(sel).forEach((el) =>
          ScrollTrigger.create({
            trigger: el, start: "top 28px", end: "bottom 28px",
            onToggle: (self) => { if (self.isActive) bar?.style.setProperty("--bar-bg", col); },
          }),
        ),
      );
    });

    const refresh = () => ScrollTrigger.refresh();
    document.fonts?.ready.then(refresh);
    window.addEventListener("load", refresh);

    return () => {
      window.removeEventListener("load", refresh);
      anchors.forEach((a) => a.removeEventListener("click", onAnchorClick));
      ctx.revert();
      gsap.ticker.remove(tick);
      lenis.destroy();
      document.body.classList.remove("is-loading");
      if (loader) loader.style.display = "none";
    };
  }, []);

  return <>{children}</>;
}
