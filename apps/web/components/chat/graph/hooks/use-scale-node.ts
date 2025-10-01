import { useEffect, useRef, useState } from "react";

export const useScaleNode = () => {
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const content = ref.current;
    const parent = content?.parentElement as HTMLElement | null;
    if (!content || !parent) return;

    let raf = 0;
    const measure = () => {
      // Available box inside the circle (minus padding already on the parent)
      const availW = parent.clientWidth;
      const availH = parent.clientHeight;

      // Measure unscaled content size
      const { scrollWidth, scrollHeight } = content;

      // Compute downscale factor if content would overflow
      const s = Math.min(1, availW / Math.max(1, scrollWidth), availH / Math.max(1, scrollHeight));

      // Avoid layout thrash; set only when the delta is meaningful
      if (Number.isFinite(s) && Math.abs(s - scale) > 0.02) {
        setScale(s);
      }
    };

    const ro = new ResizeObserver(() => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(measure);
    });

    ro.observe(parent);
    ro.observe(content);

    raf = requestAnimationFrame(measure);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
    };
  }, [scale]);

  return { ref, scale };
}
