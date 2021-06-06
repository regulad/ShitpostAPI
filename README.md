# ShitpostAPI

An API for making quick edits of media, normally memes, to create a new type of media commonly referred to as a shitpost.

## Hosting

Docker is the preferred way to host an instance of the API.

Environment Variables:

* `SHITPOST_API_PORT`: Configures the webserver port. Default is `8081`.
* `SHITPOST_API_HOST`: Configures the webserver host. Default is `0.0.0.0`.
* `SHITPOST_API_URI`: MongoDB connection URI. Default is `mongodb://localhost:27107`.
* `SHITPOST_API_DB`: MongoDB database name. Default is `shitposts`.

## API

### POST `/edit`

Form fields:

* Media:
    * Type: Bytes
    * Content: The media you wish to edit, in bytes.
    * Headers:
        * Content-Type: The MIME type of the media.
* Edits:
    * Type: String
    * Content: A JSON-Encoded string of the commands you wish to execute and their values.
    * Headers:
        * Content-Type: application/json
    
Edits example:

```json
{
  "top_text": {
    "text": "some_string"
  },
  "bottom_text": {
    "text": "another_string"
  }
}
```

### GET `/commands`

Returns JSON data detailing available commands.

Example return:

```json
{
  "commands": [
    {
      "name": "top_text",
      "parameters": [
        {
          "name": "text",
          "type": "str"
        }
      ],
      "description": "Appends text in impact font to the top of an image."
    },
    {
      "name": "bottom_text",
      "parameters": [
        {
          "name": "text",
          "type": "str"
        }
      ],
      "description": "Appends text in impact font to the bottom of an image."
    }
  ]
}
```
