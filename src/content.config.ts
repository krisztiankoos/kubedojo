import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { docsSchema } from '@astrojs/starlight/schema';
import { z } from 'astro:content';

const docsExtensions = ['markdown', 'mdown', 'mkdn', 'mkd', 'mdwn', 'md', 'mdx'];
const docsPattern = [
  `**/[^_]*.{${docsExtensions.join(',')}}`,
  `!**/*.staging.{${docsExtensions.join(',')}}`,
];

const starlightDocsLoader = {
  name: 'starlight-docs-loader',
  load: (context) =>
    glob({
      base: new URL('content/docs/', context.config.srcDir),
      pattern: docsPattern,
    }).load(context),
};

export const collections = {
  docs: defineCollection({
    loader: starlightDocsLoader,
    schema: docsSchema({
      extend: z.object({
        lab: z.object({
          id: z.string(),
          url: z.string().url(),
          duration: z.string(),
          difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
          environment: z.enum(['ubuntu', 'kubernetes']),
        }).optional(),
      }),
    }),
  }),
};
