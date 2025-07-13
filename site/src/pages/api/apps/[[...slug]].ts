import fs from 'fs';
import path from 'path';
import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
    const slug = req.query.slug ?? [];
    const segments = Array.isArray(slug) ? slug : [slug];
    const baseDir = path.resolve('./../../apps')
    const targetDir = path.join(baseDir, ..segments);

    if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
        res.status(404).json({ error: 'Not Found' });
        return;
    }
    
    const files = fs.readdirSync(targetDir).filter(file => file.endsWith('.json'));

    const apps = files.map(file => {
        const content = fs.readFileSync(path.join(targetDir, file), 'utf-8');
        return {
            name: file.replace('.join', ''),
            data: JSON.parse(content),
        };
    });
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json(apps);
}