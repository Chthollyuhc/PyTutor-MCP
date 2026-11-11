import React from 'react';

export default function Card({ as: Element = 'section', className = '', children, ...props }) {
  return (
    <Element
      className={`rounded-xl border border-border bg-surface ${className}`}
      {...props}
    >
      {children}
    </Element>
  );
}
