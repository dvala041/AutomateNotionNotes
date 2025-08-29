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
        category: str,
        author: str,
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
                        "name": category
                    }
                },
                "Author": {
                    "rich_text": [
                        {
                            "text": {
                                "content": author
                            }
                        }
                    ]
                }
            }
            
            # Create properly formatted content blocks from the summary
            content_blocks = self._format_summary_to_blocks(summary)
            
            # Add video details section
            content_blocks.extend([
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
                                    "content": f"Original Title: {video_title}\nURL: {video_url}\nDuration: {duration:.1f} seconds" if duration else f"Original Title: {video_title}\nURL: {video_url}"
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
            ])
            
            # Create the page with formatted content
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                children=content_blocks
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
    
    def _format_summary_to_blocks(self, summary: str) -> list:
        """
        Convert a plain text summary into properly formatted Notion blocks
        """
        blocks = []
        
        # Add the main summary heading
        blocks.append({
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
        })
        
        # Split the summary into lines and process line by line for better nesting
        lines = summary.split('\n')
        last_block_type = None
        
        for line in lines:
            if not line.strip():
                continue
                
            # Check for numbered list items (1., 2., 3., etc.)
            if line.strip().startswith(tuple(f'{i}.' for i in range(1, 21))):
                # Extract the content after the number
                content = line.strip()
                # Remove the number and period, keep the colon if present
                for i in range(1, 21):
                    if content.startswith(f'{i}.'):
                        content = content[len(f'{i}.'):].strip()
                        break
                
                block = {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
                
                # If the previous block was a numbered list, add sub-items as children
                if last_block_type == "numbered_list_item" and len(blocks) > 1:
                    # Add as children to the last numbered list item
                    if "children" not in blocks[-1]["numbered_list_item"]:
                        blocks[-1]["numbered_list_item"]["children"] = []
                    # But actually, Notion doesn't support children in this way, so just add normally
                
                blocks.append(block)
                last_block_type = "numbered_list_item"
                
            # Check for letter sub-items (a., b., c., etc.)
            elif line.strip().startswith(('a.', 'b.', 'c.', 'd.', 'e.', 'f.', 'g.', 'h.')):
                # Extract content after the letter
                content = line.strip()[2:].strip()
                
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                })
                last_block_type = "bulleted_list_item"
                
            # Check for bullet points (•)
            elif '•' in line:
                bullet_text = line.split('•', 1)[-1].strip()
                
                # If this bullet follows a numbered item, treat it as a sub-item
                if last_block_type == "numbered_list_item":
                    # Create a bulleted list item that will appear indented
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": bullet_text
                                    }
                                }
                            ]
                        }
                    })
                    last_block_type = "bulleted_list_item"
                else:
                    # Regular bullet point
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": bullet_text
                                    }
                                }
                            ]
                        }
                    })
                    last_block_type = "bulleted_list_item"
                    
            # Regular text line
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line.strip()
                                }
                            }
                        ]
                    }
                })
                last_block_type = "paragraph"
        
        return blocks
    
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
