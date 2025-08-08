"""
Instagram Cookie Helper

This module helps extract Instagram cookies from your browser to authenticate yt-dlp.
This is often more reliable than username/password authentication.
"""

import os
import json
from typing import Optional, Dict, Any
import browser_cookie3
import logging

logger = logging.getLogger(__name__)

class InstagramCookieHelper:
    """Helper class to manage Instagram cookies for yt-dlp"""
    
    @staticmethod
    def extract_cookies_from_browser(browser: str = 'chrome') -> Optional[str]:
        """
        Extract Instagram cookies from browser
        
        Args:
            browser: Browser name ('chrome', 'firefox', 'safari', 'edge')
        
        Returns:
            Path to cookies file or None if failed
        """
        try:
            if browser.lower() == 'chrome':
                cj = browser_cookie3.chrome(domain_name='instagram.com')
            elif browser.lower() == 'firefox':
                cj = browser_cookie3.firefox(domain_name='instagram.com')
            elif browser.lower() == 'safari':
                cj = browser_cookie3.safari(domain_name='instagram.com')
            elif browser.lower() == 'edge':
                cj = browser_cookie3.edge(domain_name='instagram.com')
            else:
                logger.error(f"Unsupported browser: {browser}")
                return None
            
            # Save cookies to temporary file
            cookies_file = os.path.join(os.getcwd(), 'instagram_cookies.txt')
            
            with open(cookies_file, 'w') as f:
                for cookie in cj:
                    if 'instagram.com' in cookie.domain:
                        f.write(f"{cookie.domain}\t{str(cookie.domain_specified).upper()}\t{cookie.path}\t{str(cookie.secure).upper()}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
            
            logger.info(f"Cookies extracted to: {cookies_file}")
            return cookies_file
            
        except Exception as e:
            logger.error(f"Failed to extract cookies from {browser}: {e}")
            return None
    
    @staticmethod
    def get_ydl_opts_with_cookies(browser: str = 'chrome') -> Dict[str, Any]:
        """
        Get yt-dlp options with browser cookies
        
        Args:
            browser: Browser to extract cookies from
        
        Returns:
            Dict with yt-dlp options including cookies
        """
        base_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': 'best',
            'noplaylist': True,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
        }
        
        # Try to use cookies from browser directly
        try:
            if browser.lower() == 'chrome':
                base_opts['cookiesfrombrowser'] = ('chrome',)
            elif browser.lower() == 'firefox':
                base_opts['cookiesfrombrowser'] = ('firefox',)
            elif browser.lower() == 'safari':
                base_opts['cookiesfrombrowser'] = ('safari',)
            elif browser.lower() == 'edge':
                base_opts['cookiesfrombrowser'] = ('edge',)
            
            logger.info(f"Using cookies from {browser}")
            return base_opts
            
        except Exception as e:
            logger.warning(f"Failed to use cookies from {browser}: {e}")
            
            # Fallback: extract cookies to file
            cookies_file = InstagramCookieHelper.extract_cookies_from_browser(browser)
            if cookies_file:
                base_opts['cookiefile'] = cookies_file
                logger.info(f"Using cookies file: {cookies_file}")
            
            return base_opts
