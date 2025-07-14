import fs from 'fs';
import path from 'path';

export async function GET() {
  const appsDir = path.resolve('./../apps/macos');
  const files = fs.readdirSync(appsDir).filter(f => f.endsWith('.json'));

  const apps = files.map(file => {
    const content = fs.readFileSync(path.join(appsDir, file), 'utf-8');
    return {
      name: file.replace('.json', ''),
      data: JSON.parse(content),
    };
  });

  return new Response(JSON.stringify(apps), {
    headers: { 'Content-Type': 'application/json' },
  });
}