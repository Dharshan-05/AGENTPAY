'use client';

import { LazyMotion, domAnimation, m } from 'framer-motion';
import { EASE } from '@/lib/motion';

interface Props {
  text: string;
  className?: string;
  delay?: number;
  stagger?: number;
  mode?: 'chars' | 'words';
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
}

export function SplitText({ text, className = '', delay = 0, stagger = 0.025, mode = 'words', as = 'span' }: Props) {
  const items = mode === 'words' ? text.split(' ') : text.split('');
  const Tag: 'h1' | 'h2' | 'h3' | 'p' | 'span' = as;

  return (
    <LazyMotion features={domAnimation}>
      <Tag className={className} aria-label={text}>
        {items.map((item, i) => (
          <m.span
            key={i}
            aria-hidden="true"
            initial={{ opacity: 0, y: '0.35em', filter: 'blur(8px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            transition={{
              duration: 0.5,
              ease: EASE.smooth,
              delay: delay + i * stagger,
            }}
            style={{ display: 'inline-block', marginRight: mode === 'words' ? '0.25em' : '0' }}
          >
            {item}
          </m.span>
        ))}
      </Tag>
    </LazyMotion>
  );
}
