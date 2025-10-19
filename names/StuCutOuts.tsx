import { Button, Rows, Text, PaintRollerIcon, MultilineInput } from "@canva/app-ui-kit";
import { FormattedMessage, useIntl } from "react-intl";
import * as styles from "styles/components.css";
import { useAddElement } from "utils/use_add_element";
import { editContent } from "@canva/design";
import { addPage } from "@canva/design";
import { upload } from "@canva/asset";
import { addElementAtPoint } from "@canva/design";
import { openDesign, type DesignEditing } from "@canva/design";
import type { TextElementAtPoint, ImageElementAtPoint } from "@canva/design";
import { CanvaError } from "@canva/error";

let textArr = [];
let rectArr = [];
let shapeArr = [];
let array = []

async function sleep(ms: number) {
  return new Promise( resolve => setTimeout(resolve, ms) );
}

export const DOCS_URL = "https://www.canva.dev/docs/apps/";

export const App = () => {

  async function shapeExample () {
    const image = await upload({
      type: "image",
      mimeType: "image/jpeg",
      url: "https://www.canva.dev/example-assets/image-import/image.jpg",
      thumbnailUrl: "https://www.canva.dev/example-assets/image-import/thumbnail.jpg",
      aiDisclosure: "none"
    });
    await addElementAtPoint({
      type: "shape",
      paths: [
        {
          d: "M 0 0 H 100 V 100 H 0 L 0 0",
          fill: {
            dropTarget: false,
            asset: {
              type: "image",
              ref: image.ref,
            },
          },
        },
      ],
      viewBox: {
        height: 100,
        width: 100,
        left: 0,
        top: 0,
      },
    });
  }

  async function readData() { //collects data on all objects in the design | e.g. text, images, etc
    // console.log('hi');
    textArr = [];
    rectArr = [];
    shapeArr = [];
    let num = 0;
    await openDesign({ type: "current_page" }, async (session) => {
      if (session.page.type !== "absolute") {
        return; // lwky idk y dis is here, if its not here then stuff breaks T_T
      }

      let shapesRefs = []
      session.page.elements.filter((element) => { // gets refs for images
        if (element.type !== "shape") return false;
    
        return element.paths.toArray().some((path) => {
          const colorFill = path.fill.colorContainer?.ref;
          // console.log('run')
          // console.log("path", path, path.fill, path.fill.mediaContainer, path.fill.mediaContainer.zg, 'here', path.fill.mediaContainer.zg.imageRef)
          shapesRefs.push(path.fill.mediaContainer.zg.imageRef)
          return path.fill.mediaContainer.zg.imageRef;
        });
      });

      // console.log("bap: ", shapesRefs)
    
      // Iterate through all elements
      session.page.elements.forEach((element) => {
        let hashed = new Map()
        // console.log(element)
        hashed["type"] = element.type;
        hashed['top'] = element.top;
        hashed['left'] = element.left;
        hashed['width'] = element.width;
        hashed['height'] = element.height;
        hashed["rotation"] = element.rotation;
        hashed["locked"] = element.locked;
        hashed["textAlign"] = element.align ===  undefined ? "center" : element.align;
        // console.log("type: ", hashed["type"]) // temp edited here
        if (hashed["type"] === "text") {
          hashed["children"] = [element.text.readPlaintext()];
          hashed["color"] = element.text["state"]["regions"][0]["formatting"]["color"];
          hashed["fontRef"] = element.text["state"]["regions"][0]["formatting"]["fontRef"];
          hashed["fontStyle"] = element.text["state"]["regions"][0]["formatting"]["fontStyle"];
          hashed["fontWeight"] = element.text["state"]["regions"][0]["formatting"]["fontWeight"];
          hashed["rotation"] = element.text["state"]["regions"][0]["formatting"]["rotation"];
          hashed["fontSize"] = element.text["state"]["regions"][0]["formatting"]["fontSize"]; // the font size is HIDDEN in the hash maps lol
          textArr.push(hashed);
      } else if (hashed["type"] === "rect") {
          hashed["ref"] = element.fill.mediaContainer?.ref.imageRef;
          rectArr.push(hashed);
      } else if (hashed['type'] === "shape") { // temp edited here
        // console.log("FINALLY: ", element.paths.toArray()[0].fill.mediaContainer.zg.imageRef)
      
          hashed["paths"] = [
            {
              d: "M 0 0 H 100 V 100 H 0 L 0 0",
              fill: {
                dropTarget: false,
                asset: {
                  type: "image",
                  ref: shapesRefs[num],
                },
              },
            },
          ],
          hashed["viewBox"] = {
            "top": 0,
            'left': 0,
            'height': 100,
            'width': 100,
          }
          shapeArr.push(hashed);
          // console.log("MA", shapeArr);
          num += 1
      }

      });
    
      // Filter specific element types
      const textElements = session.page.elements.filter(
        (element): element is DesignEditing.TextElement => element.type === "text"
      );
    
      // console.log(`Found ${textElements.length} text elements`);
      session.page.elements.forEach((element) => {
        if (element.type !== "rect") {
          return;
        }
    
        const media = element.fill.mediaContainer?.ref;
        if (media?.type === "image") {
          // console.log(`Rect has image fill: ${media.imageRef}`);
        }
      });
      // console.log(textArr)
      })}

  const addElement = useAddElement(); // idk wat this is ngl

  async function addNames() {
    let names = document.getElementById("names").value.split("\n");
    await openDesign({ type: "current_page" }, async (session) => {
      if (session.page.type !== "absolute" || session.page.locked) {
        return;
      }
    
      session.page.elements.forEach((element) => {
        if (element.type === "text") {
          element.text.replaceText(
            { index: 0, length: element.text.readPlaintext().length },
            names[0]
          );
          names.shift()
        }
      });
    
      // Apply all changes
      await session.sync();
    });
  }

  async function handleClick() {
        // Upload an image
        const result = await upload({
          type: "image",
          mimeType: "image/jpeg",
          url: "https://images.unsplash.com/photo-1606115915090-be18fea23ec7?q=80&w=765&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D0",
          thumbnailUrl:
            "https://images.unsplash.com/photo-1606115915090-be18fea23ec7?q=80&w=765&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
          aiDisclosure: "none",
        });
        // console.log(result.ref)
            // Add the image to the design
        await addElementAtPoint({
          type: "image",
          ref: result.ref,
          altText: {
            text: "Example image",
            decorative: false
          },
          height: 200,
          width: 200,
          top: 100,
          left: 600
        });
  };
  async function pastePage() { //NTS: MAKE SURE TO HAVE THE LITTLE SQUARE THINGS AT THE BOTTOM OR THE CODE DOESN'T WORK
    addPage({ // pastes all the text
      elements: shapeArr.concat(textArr),
    })
    await openDesign({ type: "current_page" }, async (session) => {
      for (let i = 0; i < rectArr.length; i++) { // deals w/ images (aka rects)
        let element = rectArr[i];
        // console.log(element);
        const rectElementState =
          session.helpers.elementStateBuilder.createRectElement({
            top: element["top"],
            left: element["left"],
            width: element["width"],
            height: element["height"],
            fill: {
              mediaContainer: {
                type: "image",
                imageRef: element["ref"],
                flipX: false,
                flipY: false,
              },
            },
          });

        session.page.elements.insertAfter(undefined, rectElementState);
        await session.sync();
      }
    })
  }

  // async function addNames(array) {
  //   let count = 0;
  //   await openDesign({ type: "current_page" }, async (session) => {
  //     session.page.elements.forEach((element) => {
  //       if (!element.locked && element.type == "text") {
  //         element.text.replaceText(
  //           { index: 0, length: element.text.readPlaintext().length },
  //           array[count],
  //         );
  //         count++
  //       }
  //     })
  //   })
  // }

  async function magic () {
    let names = document.getElementById("names").value.split("\n");
    textArr = [];
    rectArr = [];
    shapeArr = [];
    let num = 0;
    await openDesign({ type: "current_page" }, async (session) => {
      if (session.page.type !== "absolute") {
        return; // lwky idk y dis is here, if its not here then stuff breaks T_T
      }

      let shapesRefs = []
      session.page.elements.filter((element) => { // gets refs for images
        if (element.type !== "shape") return false;
    
        return element.paths.toArray().some((path) => {
          const colorFill = path.fill.colorContainer?.ref;
          // console.log('run')
          // console.log("path", path, path.fill, path.fill.mediaContainer, path.fill.mediaContainer.zg, 'here', path.fill.mediaContainer.zg.imageRef)
          shapesRefs.push(path.fill.mediaContainer.zg.imageRef)
          return path.fill.mediaContainer.zg.imageRef;
        });
      });

      // console.log("bap: ", shapesRefs)
    
      // Iterate through all elements
      session.page.elements.forEach((element) => {
        let hashed = new Map()
        // console.log(element)
        hashed["type"] = element.type;
        hashed['top'] = element.top;
        hashed['left'] = element.left;
        hashed['width'] = element.width;
        hashed['height'] = element.height;
        hashed["rotation"] = element.rotation;
        hashed["locked"] = element.locked;
        hashed["textAlign"] = element.align ===  undefined ? "center" : element.align;
        // console.log("type: ", hashed["type"]) // temp edited here
        if (hashed["type"] === "text") {
          hashed["children"] = [element.text.readPlaintext()];
          hashed["color"] = element.text["state"]["regions"][0]["formatting"]["color"];
          hashed["fontRef"] = element.text["state"]["regions"][0]["formatting"]["fontRef"];
          hashed["fontStyle"] = element.text["state"]["regions"][0]["formatting"]["fontStyle"];
          hashed["fontWeight"] = element.text["state"]["regions"][0]["formatting"]["fontWeight"];
          hashed["rotation"] = element.text["state"]["regions"][0]["formatting"]["rotation"];
          hashed["fontSize"] = element.text["state"]["regions"][0]["formatting"]["fontSize"]; // the font size is HIDDEN in the hash maps lol
          textArr.push(hashed);
      } else if (hashed["type"] === "rect") {
          hashed["ref"] = element.fill.mediaContainer?.ref.imageRef;
          rectArr.push(hashed);
      } else if (hashed['type'] === "shape") { // temp edited here
        // console.log("FINALLY: ", element.paths.toArray()[0].fill.mediaContainer.zg.imageRef)
      
          hashed["paths"] = [
            {
              d: "M 0 0 H 100 V 100 H 0 L 0 0",
              fill: {
                dropTarget: false,
                asset: {
                  type: "image",
                  ref: shapesRefs[num],
                },
              },
            },
          ],
          hashed["viewBox"] = {
            "top": 0,
            'left': 0,
            'height': 100,
            'width': 100,
          }
          shapeArr.push(hashed);
          // console.log("MA", shapeArr);
          num += 1
      }

      });
    
      // Filter specific element types
      const textElements = session.page.elements.filter(
        (element): element is DesignEditing.TextElement => element.type === "text"
      );
    
      // console.log(`Found ${textElements.length} text elements`);
      session.page.elements.forEach((element) => {
        if (element.type !== "rect") {
          return;
        }
    
        const media = element.fill.mediaContainer?.ref;
        if (media?.type === "image") {
          // console.log(`Rect has image fill: ${media.imageRef}`);
        }
      });
      // console.log(textArr)
      })
    
    
    let textArrLength = textArr.length;
    let savedNamesLength = names.length; // saved because we're changing the length of names throught the script
    for (let j = 0; j < textArrLength - (savedNamesLength % textArrLength); j++) names.push("Filler Data, Delete Me") // produces filler data so it can work fr
    console.log(names)

    for (let i = 0; i < savedNamesLength; i += textArrLength) {
      console.log("deets: ", names.length, i, textArrLength, names.length)
      try {
      addPage({ // pastes all the text
        elements: shapeArr.concat(textArr), // fyi shapeArr has to be in front because if not the text will come behind it
      })

      await openDesign({ type: "current_page" }, async (session) => {
          await session.page.elements.forEach((element) => {
            element.children = names[0]
            if (element.type === "text") {
              element.text.replaceText(
                { index: 0, length: element.text.readPlaintext().length },
                names[0]
              );
              names.shift()
            }
          });
          await session.sync();
        })
      await openDesign({ type: "current_page" }, async (session) => {
        console.log("ran")
        
        for (let i = 0; i < rectArr.length; i++) { // deals w/ images (aka rects)
          let element = rectArr[i];
          // console.log(element);
          const rectElementState =
            await session.helpers.elementStateBuilder.createRectElement({
              top: element["top"],
              left: element["left"],
              width: element["width"],
              height: element["height"],
              fill: {
                mediaContainer: {
                  type: "image",
                  imageRef: element["ref"],
                  flipX: false,
                  flipY: false,
                },
              },
            });
  
          await session.page.elements.insertAfter(undefined, rectElementState);
        }
        await session.sync();
        console.log("arr: ", names);
      })
    }
      catch (error) {
      console.log("error caught, ith val: ", i)
      i -= textArrLength
      console.log("updated value: ", i)
      if (error instanceof CanvaError && error.code === "rate_limited") {
        console.error();
        console.log(error);
        console.log("ran err");
        await sleep(4500);
        await openDesign({ type: "current_page" }, async (session) => {
          console.log("ran")
          
          for (let i = 0; i < rectArr.length; i++) { // deals w/ images (aka rects)
            let element = rectArr[i];
            // console.log(element);
            const rectElementState =
              await session.helpers.elementStateBuilder.createRectElement({
                top: element["top"],
                left: element["left"],
                width: element["width"],
                height: element["height"],
                fill: {
                  mediaContainer: {
                    type: "image",
                    imageRef: element["ref"],
                    flipX: false,
                    flipY: false,
                  },
                },
              });
    
            await session.page.elements.insertAfter(undefined, rectElementState);
  
            await session.sync();
          }
          console.log("arr: ", names);
        })
      }
    }
      await sleep(1000) // sleeps for 1s bc of rate lim
    }
  }

  // don't edit wtv this is
  const intl = useIntl();

  return (
    <div className={styles.scrollContainer}>
      <Rows spacing="2u">
        <Text>
          <FormattedMessage
            defaultMessage="
              To make changes to this app, edit the <code>src/app.tsx</code> file,
              then close and reopen the app in the editor to preview the changes.
            "
            description="Instructions for how to make changes to the app. Do not translate <code>src/app.tsx</code>."
            values={{
              code: (chunks) => <code>{chunks}</code>,
            }}
          />
        </Text>
        <Button variant="primary" onClick={addNames} stretch>
          {intl.formatMessage({
            defaultMessage: "Add names",
            description:
              "Button text to do something cool. Creates a new text element when pressed.",
          })}
        </Button>
      <Button variant="primary" onClick={handleClick} stretch>
        {intl.formatMessage({
          defaultMessage: "Add image from external URL",
          description:
            "Button text to add an image from an external URL when pressed.",}
        )}
        </Button>
<MultilineInput // dont question the red line
        placeholder="Type something..."
        id="names"
/>
<Button variant="primary" onClick={readData} stretch>
        {intl.formatMessage({
          defaultMessage: "copy page",
          description:
            "copies all pages contents",}
        )}
        </Button>
        <Button variant="primary" onClick={pastePage} stretch>
        {intl.formatMessage({
          defaultMessage: "paste page",
          description:
            "copies all pages contents",}
        )}
        </Button>
        <Button variant="primary" onClick={magic} stretch>
          {intl.formatMessage({
            defaultMessage: "Magic",
            description: "the MAIN COURSE",}
            )}
          </Button>
          <Button variant="primary" onClick={shapeExample} stretch>
          {intl.formatMessage({
            defaultMessage: "shape example",
            description: "shape",}
            )}
          </Button>
      </Rows>
    </div>
  );
};

// prob helpful

// // Assuming you have access to the Canva design context
// canva.design.addPage({
//   copyPage: {
//     pageId: 'your_source_page_id' // Replace with the ID of the page you want to duplicate
//   }
// });
