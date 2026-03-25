import { getCollection } from 'astro:content';

export async function GET({params, request}) {
  const docs = await getCollection('docs');
  return new Response(
    JSON.stringify(docs.map(d => ({ id: d.id, slug: d.slug || d?.data?.slug }))), {
      status: 200,
      headers: {
        "Content-Type": "application/json"
      }
    }
  );
}
