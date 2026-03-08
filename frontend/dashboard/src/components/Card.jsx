import React from "react";

function Card({ title, children }) {
  return (
    <section className="rounded-xl bg-white p-6 shadow-md">
      {title ? <h2 className="mb-4 text-lg font-semibold text-slate-900">{title}</h2> : null}
      <div className="space-y-4">{children}</div>
    </section>
  );
}

export default Card;
