About
FLUX.1 Redux [schnell], remix your images at turbo-speed with FLUX model.

1. Calling the API
#
Install the client
#
The client provides a convenient way to interact with the model API.


pip install fal-client
Setup your API Key
#
Set FAL_KEY as an environment variable in your runtime.


export FAL_KEY="YOUR_API_KEY"
Submit a request
#
The client API handles the API submit protocol. It will handle the request status updates and return the result when the request is completed.

PythonPython (async)

import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/flux/schnell/redux",
    arguments={
        "image_url": "https://fal.media/files/kangaroo/acQvq-Kmo2lajkgvcEHdv.png"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
2. Authentication
#
The API uses an API Key for authentication. It is recommended you set the FAL_KEY environment variable in your runtime when possible.

API Key
#
Protect your API Key
When running code on the client-side (e.g. in a browser, mobile app or GUI applications), make sure to not expose your FAL_KEY. Instead, use a server-side proxy to make requests to the API. For more information, check out our server-side integration guide.

3. Queue
#
Long-running requests
For long-running requests, such as training jobs or models with slower inference times, it is recommended to check the Queue status and rely on Webhooks instead of blocking while waiting for the result.

Submit a request
#
The client API provides a convenient way to submit requests to the model.

PythonPython (async)

import fal_client

handler = fal_client.submit(
    "fal-ai/flux/schnell/redux",
    arguments={
        "image_url": "https://fal.media/files/kangaroo/acQvq-Kmo2lajkgvcEHdv.png"
    },
    webhook_url="https://optional.webhook.url/for/results",
)

request_id = handler.request_id
Fetch request status
#
You can fetch the status of a request to check if it is completed or still in progress.

PythonPython (async)

status = fal_client.status("fal-ai/flux/schnell/redux", request_id, with_logs=True)
Get the result
#
Once the request is completed, you can fetch the result. See the Output Schema for the expected result format.

PythonPython (async)

result = fal_client.result("fal-ai/flux/schnell/redux", request_id)
4. Files
#
Some attributes in the API accept file URLs as input. Whenever that's the case you can pass your own URL or a Base64 data URI.

Data URI (base64)
#
You can pass a Base64 data URI as a file input. The API will handle the file decoding for you. Keep in mind that for large files, this alternative although convenient can impact the request performance.

Hosted files (URL)
#
You can also pass your own URLs as long as they are publicly accessible. Be aware that some hosts might block cross-site requests, rate-limit, or consider the request as a bot.

Uploading files
#
We provide a convenient file storage that allows you to upload files and use them in your requests. You can upload files using the client API and use the returned URL in your requests.

PythonPython (async)

url = fal_client.upload_file("path/to/file")
Read more about file handling in our file upload guide.

5. Schema
#
Input
#
image_url string
The URL of the image to generate an image from.

num_inference_steps integer
The number of inference steps to perform. Default value: 4

image_size ImageSize | Enum
The size of the generated image. Default value: landscape_4_3

Possible enum values: square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9

Note: For custom image sizes, you can pass the width and height as an object:


"image_size": {
  "width": 1280,
  "height": 720
}
seed integer
The same seed and the same prompt given to the same version of the model will output the same image every time.

sync_mode boolean
If True, the media will be returned as a data URI and the output data won't be available in the request history.

num_images integer
The number of images to generate. Default value: 1

enable_safety_checker boolean
If set to true, the safety checker will be enabled. Default value: true

output_format OutputFormatEnum
The format of the generated image. Default value: "jpeg"

Possible enum values: jpeg, png

acceleration AccelerationEnum
The speed of the generation. The higher the speed, the faster the generation. Default value: "none"

Possible enum values: none, regular, high


{
  "image_url": "https://fal.media/files/kangaroo/acQvq-Kmo2lajkgvcEHdv.png",
  "num_inference_steps": 4,
  "image_size": "landscape_4_3",
  "num_images": 1,
  "enable_safety_checker": true,
  "output_format": "jpeg",
  "acceleration": "none"
}
Output
#
images list<Image>
The generated image files info.

timings Timings
seed integer
Seed of the generated Image. It will be the same value of the one passed in the input or the randomly generated that was used in case none was passed.

has_nsfw_concepts list<boolean>
Whether the generated images contain NSFW concepts.

prompt string
The prompt used for generating the image.


{
  "images": [
    {
      "url": "",
      "content_type": "image/jpeg"
    }
  ],
  "prompt": ""
}
Other types
#
Image
#
url string
width integer
height integer
content_type string
Default value: "image/jpeg"

ImageSize
#
width integer
The width of the generated image. Default value: 512

height integer
The height of the generated image. Default value: 512

