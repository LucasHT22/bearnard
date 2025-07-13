import fs from 'fs';
import path from 'path';
import type { APIRoute } from 'next';

const baseDir = path.resolve('./../../apps');

function collectJsonFiles(dir: string, relParts: string[] = []) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    let results: any[] = [];

    for (const entry of entries) {
        if (entry.isDirectory()) {
            results = results.concat(collectJsonFiles(path.join(dir, entry.name), [...relParts, entry.name]),);
        } else if (entry.isFile() && entry.name.endsWith('.json')) {
            const content = fs.readFileSync(path.join(dir, entry.name), 'utf-8');
            results.push({
                name: entry.name.replace(/\.json$/i, ''),
                path: relParts,
                data: JSON.parse(content),
            });
        }
    }
    return results;
}

export const GET: APIRoute = async ({ params }) => {
    const slug = params.slug ?? [];
    const segments = Array.isArray(slug) ? slug : [slug];
    const targetDir = path.join(baseDir, ...segments);

    if (!targetDir.startsWith(baseDir)) {
        return new Response(JSON.stringify({ error: 'Invalid path' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
        });
    }

    if (segments.length === 0) {
        const all = collectJsonFiles(baseDir);
        return new Response(JSON.stringify(all), {
            headers: { 'Content-Type': 'application/json' },
        });
    }

    if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
        return new Response(JSON.stringify({ error: 'Not found' }), {
            status: 404,
            headers: { 'Content-Type': 'application/json' },
        });
    }

    const files = fs.readdirSync(targetDir).filter(f => f.endsWith('.json'));
    const apps = files.map(file => ({
        name: file.replace(/\.json$/i, ''),
    path: segments,
    data: JSON.parse(fs.readFileSync(path.join(targetDir, file), 'utf-8')),
    }));

    return new Response(JSON.stringify(apps), {
        headers: { 'Content-Type': 'application/json' },
    });
}