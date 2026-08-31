# Guide e video

`sync_youtube.py` usa soltanto YouTube Data API v3 e legge la chiave da `YOUTUBE_API_KEY` nell'ambiente. La chiave non viene letta da file del sito, non viene stampata e non viene salvata nel JSON.

`build_guides.py` trasforma `data/youtube-videos.json` in archivio Guide, pagine statiche dei video, sitemap e robots.txt.

Le categorie vengono assegnate soltanto da parole presenti nel titolo, nella descrizione o nei tag: Windows, Linux e Intelligenza artificiale. Se non esiste un indizio chiaro, il video resta in Altro.

Esecuzione locale:

```bash
export YOUTUBE_API_KEY='valore-mantenuto-fuori-dal-progetto'
python3 scripts/sync_youtube.py
python3 scripts/build_guides.py
```
