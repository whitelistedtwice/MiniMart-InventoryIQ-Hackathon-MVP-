/*
  Simple historical demand chart.

  Maps the backend's `sales_history` pairs into a lightweight SVG line. It
  shows only observed units sold per day — no forecasting, no calculations.
  Missing/short history gets a clear message instead of a fake chart.
*/

type Point = [string, number];

const WIDTH = 720;
const HEIGHT = 220;
const PAD_X = 46;
const PAD_Y = 18;

function shortDate(iso: string): string {
  const [, month, day] = iso.split("-").map(Number);
  if (!month || !day) return iso;
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${day} ${months[month - 1] ?? month}`;
}

export function SalesTrendChart({ points }: { points: Point[] }) {
  if (points.length < 2) {
    return (
      <p className="py-10 text-center text-sm text-muted">
        Not enough sales history to show a trend yet.
      </p>
    );
  }

  const values = points.map(([, value]) => value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const lastX = PAD_X + (points.length - 1) * ((WIDTH - PAD_X * 2) / (points.length - 1));

  const coords = points.map(([, value], index) => {
    const x = PAD_X + index * ((WIDTH - PAD_X * 2) / (points.length - 1));
    const y = PAD_Y + (1 - (value - min) / range) * (HEIGHT - PAD_Y * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const baseline = HEIGHT - PAD_Y;
  const firstDate = shortDate(points[0][0]);
  const lastDate = shortDate(points[points.length - 1][0]);

  return (
    <figure>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label={`Units sold from ${firstDate} to ${lastDate}, between ${min} and ${max} units per day`}
        className="h-auto w-full"
      >
        <line x1={PAD_X} y1={PAD_Y} x2={lastX} y2={PAD_Y} className="stroke-line" strokeWidth={1} />
        <line x1={PAD_X} y1={baseline} x2={lastX} y2={baseline} className="stroke-line" strokeWidth={1} />

        <polygon
          points={`${PAD_X},${baseline} ${coords.join(" ")} ${lastX},${baseline}`}
          className="fill-brand-soft"
        />
        <polyline
          points={coords.join(" ")}
          fill="none"
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="stroke-brand"
        />

        <text x={PAD_X - 8} y={PAD_Y + 4} textAnchor="end" className="fill-muted text-[11px]">
          {max}
        </text>
        <text x={PAD_X - 8} y={baseline + 4} textAnchor="end" className="fill-muted text-[11px]">
          {min}
        </text>
        <text x={PAD_X} y={HEIGHT - 2} className="fill-muted text-[11px]">
          {firstDate}
        </text>
        <text x={lastX} y={HEIGHT - 2} textAnchor="end" className="fill-muted text-[11px]">
          {lastDate}
        </text>
      </svg>
      <figcaption className="mt-2 text-xs text-muted">
        Observed units sold per day.
      </figcaption>
    </figure>
  );
}
