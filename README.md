<div align="center">
<br />
<img src="/site/public/bearnard.png" width="300">
<br />
<h1>Bearnard (Currently only Windows!)</h1>
<p>A robust, reliable and universal system to use Wakatime in almost any App.</p>
<p>Supporting 27 different applications and counting.</p>
</div>

## Requirements
Open `cmd`, and run:
```pip install psutil pygetwindow pyautogui flask jsonify```

## How to use?

Check [Bearnard](https://bearnard.devlucas.page)

## Why?

It all started when I saw `@Ruby`'s message in Hackclub Slack:

![](https://hc-cdn.hel1.your-objectstorage.com/s/v3/44717835baa50c8142934a877a0af0276202c2c4_image.png)

Why not take the challenge?

I started by integrating WakaTime with DaVinci Resolve, and you can check out the code [here!](https://github.com/LucasHT22/davinci-resolve-wakatime/)

Later on, `@guac md` reached out asking for tips on building a WakaTime plugin for Krita. While brainstorming a solution, I realized the DaVinci approach, relying on temp files, wouldn’t work here. We needed something more robust, universal, and trackable.

The answer is: Process tracking. Every app runs as a system process, so why not use that as a reliable source of activity?

From that idea, General WakaTime was born, a cross-platform tracker that now supports 27 different applications and counting.

Shoutout to Ruby for name suggestion!