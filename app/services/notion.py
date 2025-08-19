from notion_client import Client
from app.config import settings as config
from typing import Dict, Any, Optional
import datetime

class NotionService:
    def __init__(self):
        self.client = Client(auth=config.notion_api_key)
    
    def create_page_in_database(
        self, 
        database_id: str, 
        title: str, 
        summary: str, 
        transcript: str, 
        video_url: str,
        duration: Optional[float] = None,
        video_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new page in a Notion database with the summarized content
        """
        try:
            # Prepare properties for the new page based on the actual database schema
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.datetime.now().isoformat()
                    }
                },
                "Category": {
                    "select": {
                        "name": "Video Summary"
                    }
                }
            }
            
            # Create the page with transcript and summary as content
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Summary"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": summary
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Video Details"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Video URL: {video_url}"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Original Title: {video_title or 'N/A'}"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Duration: {duration or 'N/A'} seconds"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Full Transcript"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": transcript
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            
            return {
                "success": True,
                "page_id": page["id"],
                "page_url": page["url"],
                "message": "Successfully created Notion page"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Notion page: {str(e)}"
            }
    
    def list_databases(self) -> Dict[str, Any]:
        """
        List all databases that the integration has access to
        """
        try:
            response = self.client.search(
                filter={
                    "property": "object",
                    "value": "database"
                }
            )
            
            databases = []
            for db in response["results"]:
                databases.append({
                    "id": db["id"],
                    "title": db.get("title", [{}])[0].get("plain_text", "Untitled"),
                    "url": db["url"]
                })
            
            return {
                "success": True,
                "databases": databases
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list databases: {str(e)}"
            }
    
    def get_database_properties(self, database_id: str) -> Dict[str, Any]:
        """
        Get the properties schema of a database to understand its structure
        """
        try:
            database = self.client.databases.retrieve(database_id=database_id)
            
            properties = {}
            for prop_name, prop_data in database["properties"].items():
                properties[prop_name] = {
                    "type": prop_data["type"],
                    "id": prop_data["id"]
                }
            
            return {
                "success": True,
                "properties": properties,
                "title": database.get("title", [{}])[0].get("plain_text", "Untitled")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get database properties: {str(e)}"
            }
