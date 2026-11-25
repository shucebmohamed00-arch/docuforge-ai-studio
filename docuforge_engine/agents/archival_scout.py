"""
DocuForge Multi-Agent Graphics Engine - Agent 1: Archival Scout Agent
Searches public-domain archives (Wikimedia Commons, Internet Archive, open repositories)
for authentic historical photographs, document scans, and corporate logos.
"""
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
from ..core.base_agent import BaseAgent

class ArchivalScoutAgent(BaseAgent):
    def __init__(self, cache_dir: Optional[Path] = None):
        super().__init__(
            name="scout",
            role="Archival Asset Researcher & Scout",
            description="Searches Wikimedia Commons and open archives for high-res authentic historical photos and documents."
        )
        self.cache_dir = cache_dir or (Path("c:/Users/Shueb/Desktop/youtu") / "data" / "media" / "scouted_assets")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = "DocuForgeEngine/2.0 (Historical Documentary Research; contact: info@docuforge.ai)"

    def search_wikimedia(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Queries Wikimedia Commons API for authentic media matching the query.
        """
        self.log(f"Searching Wikimedia Commons for '{query}' (limit={limit})...")
        encoded_query = urllib.parse.quote(query)
        search_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&list=search"
            f"&srsearch={encoded_query}&srnamespace=6&format=json&srlimit={limit}"
        )
        req = urllib.request.Request(search_url, headers={"User-Agent": self.user_agent})
        
        results = []
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
                search_items = data.get("query", {}).get("search", [])

            for item in search_items:
                title = item.get("title")
                # Query detailed image info for each hit
                info_url = (
                    f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}"
                    f"&prop=imageinfo&iiprop=url|size|mime|extmetadata&format=json"
                )
                info_req = urllib.request.Request(info_url, headers={"User-Agent": self.user_agent})
                with urllib.request.urlopen(info_req, timeout=12) as info_res:
                    info_data = json.loads(info_res.read().decode("utf-8"))
                    pages = info_data.get("query", {}).get("pages", {})
                    for _, page in pages.items():
                        image_info_list = page.get("imageinfo", [])
                        if image_info_list:
                            info = image_info_list[0]
                            url = info.get("url")
                            width = info.get("width", 0)
                            height = info.get("height", 0)
                            mime = info.get("mime", "")
                            
                            # Filter for usable high-res image formats
                            if width >= 800 and height >= 600 and ("jpeg" in mime or "png" in mime or "jpg" in mime):
                                results.append({
                                    "title": title.replace("File:", ""),
                                    "url": url,
                                    "width": width,
                                    "height": height,
                                    "mime": mime
                                })
        except Exception as e:
            self.log(f"Search query error: {e}", level="ERROR")

        self.log(f"Found {len(results)} high-resolution authentic candidate assets for '{query}'.")
        return results

    def download_asset(self, item: Dict[str, Any], custom_filename: Optional[str] = None) -> Optional[Path]:
        """
        Downloads the candidate image, validates integrity, and saves to the scout cache.
        """
        url = item.get("url")
        if not url:
            return None

        ext = ".jpg" if "jpeg" in item.get("mime", "") or "jpg" in item.get("mime", "") else ".png"
        safe_name = custom_filename or "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in item.get("title", "asset"))[:40]
        out_path = self.cache_dir / f"{safe_name}{ext}"

        if out_path.exists() and out_path.stat().st_size > 10000:
            self.log(f"Asset already cached locally: {out_path.name}")
            return out_path

        self.log(f"Downloading authentic asset: {item.get('title')} ({item.get('width')}x{item.get('height')})...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=20) as response, open(out_path, "wb") as f:
                f.write(response.read())

            # Validate that PIL can read the image
            with Image.open(out_path) as img:
                w, h = img.size
                if w < 600 or h < 400:
                    self.log(f"Asset failed minimum resolution gate ({w}x{h}), discarding.", level="WARNING")
                    out_path.unlink(missing_ok=True)
                    return None

            self.log(f"Successfully saved and verified asset: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")
            return out_path
        except Exception as e:
            self.log(f"Download failed for {url}: {e}", level="ERROR")
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            return None

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task parameters:
        - query: str (search term e.g. "Swissair MD-11 Zurich")
        - limit: int (candidate count, default 3)
        - auto_download: bool (whether to download the best candidate)
        """
        query = task.get("query", "Swissair")
        limit = task.get("limit", 3)
        candidates = self.search_wikimedia(query, limit=limit)
        
        downloaded = []
        if task.get("auto_download", True) and candidates:
            for item in candidates[:task.get("download_count", 1)]:
                p = self.download_asset(item)
                if p:
                    downloaded.append(str(p))

        return {
            "status": "success" if candidates else "empty",
            "query": query,
            "candidates_found": len(candidates),
            "candidates": candidates,
            "downloaded_files": downloaded
        }
