import os.path #btw dont listen to most of the comments unless they say [human made comment]
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import uuid

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/presentations"]

EMU_PER_INCH = 914400
PT_PER_INCH = 72
EMU_PER_PT = EMU_PER_INCH / PT_PER_INCH

def get_slides_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("slides", "v1", credentials=creds)

def main(word_list, img):
    service = get_slides_service()

    try:
        new_presentation_title = "Image Grid with Overlay Text"
        presentation_body = {
            'title': new_presentation_title
        }
        new_presentation = service.presentations().create(body=presentation_body).execute()
        presentation_id = new_presentation.get('presentationId')
        print(f"Created presentation with ID: {presentation_id}")
        print(f"Link: https://docs.google.com/presentation/d/{presentation_id}/edit")

        image_data = []
        for i in range(len(word_list)): # Enough for 3 slides of 8 images
            image_url = img
            overlay_text = word_list[i] +'.' #f"Pic {i+1}" # Short text for overlay
            image_data.append((image_url, overlay_text))

        images_per_slide = 8 # For a 2x4 grid

        # --- Define Grid Layout Parameters (in EMUs) ---
        SLIDE_WIDTH_EMU = 9144000
        SLIDE_HEIGHT_EMU = 5143500

        TARGET_IMAGE_WIDTH_INCHES = 2.2
        TARGET_IMAGE_HEIGHT_INCHES = 2.2 

        IMAGE_WIDTH_EMU = int(TARGET_IMAGE_WIDTH_INCHES * EMU_PER_INCH)
        IMAGE_HEIGHT_EMU = int(TARGET_IMAGE_HEIGHT_INCHES * EMU_PER_INCH)

        horizontal_spacing = int(0.2 * EMU_PER_INCH)
        vertical_spacing = int(0.2 * EMU_PER_INCH)
        
        # Define the height for the overlay text box (e.g., enough for 1-2 lines of text)
        overlay_text_box_height_emu = int(0.5 * EMU_PER_INCH) 

        # No separate caption below image, so element_total_height is just image height + vert_spacing
        element_total_height = IMAGE_HEIGHT_EMU + int(0.05 * EMU_PER_INCH) # A small gap if needed, or zero

        grid_content_width = (IMAGE_WIDTH_EMU * 4) + (horizontal_spacing * 3)
        grid_content_height = (element_total_height * 2) + (vertical_spacing * 1) 

        left_margin_emu = (SLIDE_WIDTH_EMU - grid_content_width) / 2
        top_margin_emu = (SLIDE_HEIGHT_EMU - grid_content_height) / 2
        
        if left_margin_emu < 0 or top_margin_emu < 0:
            print("Warning: Content might be too large for the slide. Adjust TARGET_IMAGE_WIDTH/HEIGHT or spacing.")

        all_batch_requests = []
        slide_count = 0

        # --- Add a Main Title Slide ---
        title_slide_id = f"s_title_{uuid.uuid4().hex[:12]}"
        all_batch_requests.append({
            'createSlide': {
                'objectId': title_slide_id,
                'insertionIndex': 0, 
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE'
                }
            }
        })
        # Add title text
        title_element_id = f"title_text_{uuid.uuid4().hex[:16]}"
        all_batch_requests.append({
            'createShape': {
                'objectId': title_element_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': title_slide_id,
                    'size': {
                        'width': {'magnitude': SLIDE_WIDTH_EMU * 0.8, 'unit': 'EMU'},
                        'height': {'magnitude': 1.5 * EMU_PER_INCH, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': SLIDE_WIDTH_EMU * 0.1, 
                        'translateY': SLIDE_HEIGHT_EMU * 0.3,
                        'unit': 'EMU'
                    }
                }
            }
        })
        all_batch_requests.append({
            'insertText': {
                'objectId': title_element_id,
                'text': new_presentation_title
            }
        })
        all_batch_requests.append({ 
            'updateParagraphStyle': {
                'objectId': title_element_id,
                'style': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        })


        # --- Loop through image data and create slides/images/overlay text ---
        for i in range(0, len(image_data), images_per_slide):
            slide_count += 1
            current_slide_id = f"s_{uuid.uuid4().hex[:12]}"

            all_batch_requests.append({
                'createSlide': {
                    'objectId': current_slide_id,
                    'insertionIndex': slide_count 
                }
            })

            current_slide_elements = image_data[i : i + images_per_slide]

            for j, (image_url, overlay_text) in enumerate(current_slide_elements):
                row = j // 4
                col = j % 4

                # Calculate X and Y coordinates for the image
                x_pos_image = int(left_margin_emu + col * (IMAGE_WIDTH_EMU + horizontal_spacing))
                y_pos_image = int(top_margin_emu + row * (element_total_height + vertical_spacing))

                image_element_id = f"img_{uuid.uuid4().hex[:16]}"

                all_batch_requests.append({
                    'createImage': {
                        'objectId': image_element_id,
                        'url': image_url,
                        'elementProperties': {
                            'pageObjectId': current_slide_id,
                            'size': {
                                'width': {'magnitude': IMAGE_WIDTH_EMU, 'unit': 'EMU'},
                                'height': {'magnitude': IMAGE_HEIGHT_EMU, 'unit': 'EMU'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': x_pos_image,
                                'translateY': y_pos_image,
                                'unit': 'EMU'
                            }
                        }
                    }
                })

                # --- Add Overlay Text Box in the middle of the Image ---
                overlay_text_box_id = f"overlay_{uuid.uuid4().hex[:16]}"
                
                # Calculate position to center text box over the image
                # Text box width will be the same as image width
                # Text box height will be defined by overlay_text_box_height_emu
                
                x_pos_overlay_text = x_pos_image # Align left with image
                # Calculate Y to center vertically over image
                y_pos_overlay_text = int(y_pos_image + (IMAGE_HEIGHT_EMU / 2) - (overlay_text_box_height_emu )) # prev line: int(y_pos_image + (IMAGE_HEIGHT_EMU / 2) - (overlay_text_box_height_emu / 2)) #straight up js '/2' on overlay_text_box_height_emu [human made comment]

                all_batch_requests.append({ #creates the textbox [human made comment]
                    'createShape': {
                        'objectId': overlay_text_box_id,
                        'shapeType': 'TEXT_BOX',
                        'elementProperties': {
                            'pageObjectId': current_slide_id,
                            'size': {
                                'width': {'magnitude': IMAGE_WIDTH_EMU, 'unit': 'EMU'}, # Same width as image
                                'height': {'magnitude': overlay_text_box_height_emu, 'unit': 'EMU'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': x_pos_overlay_text,
                                'translateY': y_pos_overlay_text - y_pos_overlay_text * 0.1, #btw the "- y_pos_overlay_text * 0.1" makes it go slightly higher
                                'unit': 'EMU'
                            }
                        },
                    }
                })
                all_batch_requests.append({ #puts the words in the text box using its ID [human made comment]
                    'insertText': {
                        'objectId': overlay_text_box_id,
                        'text': overlay_text
                    }
                })
                all_batch_requests.append({ # Center the overlay text horizontally
                    'updateParagraphStyle': {
                        'objectId': overlay_text_box_id,
                        'style': {
                            'alignment': 'CENTER'
                        },
                        'fields': 'alignment'
                    }
                })
                all_batch_requests.append({ # updates the text style (currently just the color) of the overlay text box [human made comment]
                    'updateTextStyle': {
                        'objectId': overlay_text_box_id,
                        'textRange': { # This specifies which text to apply the style to
                            'type': 'ALL' # Apply to all text in the object
                        },
                        'style': {
                            'foregroundColor': {
                                'opaqueColor': {
                                    'rgbColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    }
                                }
                            }
                            # You can add other style properties here like 'bold': True, 'fontSize': {'magnitude': 24, 'unit': 'PT'}
                        },
                        'fields': 'foregroundColor' # Crucially, specify the fields you are updating
                    }
                })
                # Optional: Add a text shadow for readability
                all_batch_requests.append({
                    'updateShapeProperties': {
                        'objectId': overlay_text_box_id,
                        'shapeProperties': {
                            'shadow': {
                                'type': 'OUTER',
                                'transform': {
                                    'scaleX': 1,
                                    'scaleY': 1,
                                    'shearX': 0,
                                    'shearY': 0,
                                    'translateX': 10000,
                                    'translateY': 10000,
                                    'unit': 'EMU'
                                },
                                'blurRadius': {'magnitude': 50000, 'unit': 'EMU'},
                                'alpha': 0.7, # 70% opacity
                            }
                        },
                        'fields': 'shadow'
                    }
                })


            # Existing slide number text box remains (adjust position to avoid collision)
            text_box_id = f"txt_{uuid.uuid4().hex[:16]}"
            all_batch_requests.append({
                'createShape': {
                    'objectId': text_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': current_slide_id,
                        'size': {
                            'width': {'magnitude': SLIDE_WIDTH_EMU / 4, 'unit': 'EMU'},
                            'height': {'magnitude': 0.5 * EMU_PER_INCH, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': SLIDE_WIDTH_EMU - (SLIDE_WIDTH_EMU / 4) - (0.2 * EMU_PER_INCH),
                            'translateY': int(0.2 * EMU_PER_INCH),
                            'unit': 'EMU'
                        },
                    }
                }
            })


        print(f"Sending {len(all_batch_requests)} requests in a single batch update...")
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': all_batch_requests}
        ).execute()
        print(f"Batch update complete. {len(response.get('replies'))} replies received.")

    except HttpError as err:
        print(err)

words = ["who","lives","in","a","pineapple","under","the","sea","spongebob","squarepants",
         "absorbent","and","yellow","and","porous","is","he", "if", "nautical", "nonsense",
         "be", "something", "you", "wish", "then", "jump", "on", "the", "deck", "and",
         "flop", "like", "a", "fish"]
img = "https://picsum.photos/200/300"
if __name__ == "__main__":
    main(words, img)
