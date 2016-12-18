Examples of JSON objects
========================

Data Structures
---------------

### Motions

There are three types of Motion objects.

#### **Stroke**

**Strokes** define how the machine fucks. **Stroke** objects have two attributes,
`position` and `speed`. Both are percentage values, between `0` and `1`.
The actual driver for the device interprets and converts these accordingly.

`position` defines the percentage of extension: `0` is completely retracted, `1` is completely extended.

`speed` defines the percentage of speed for the stroke, again from a minimum of `0` to a maximum of `1`.

In the near future, either `speed` may be expanded to allow for motion profiles, or an additional attribute may be
added to control the 'quality' of the stroke, i.e. stopping gently or suddenly.

##### Example **Stroke** JSON:

`{"position": 0.69, "speed": 0.42}`

#### **Wait**

`Wait` objects are used to pause between **Strokes** or **Patterns**.
A `Wait` has one attribute, `duration`.

`duration` is the number of seconds to pause before the next **Stroke**.

##### Example **Wait** JSON:

`{"duration": 1.5}`

#### **Pattern**

**Patterns** are groupings of motions that are cycled through in order to control the fucking machine.
**Pattern** objects have two attributes, `cycles` and `motions`.

`cycles` is a number between `0` and `Infinity`, inclusive.
A value of `0` causes the `cycle` to be skipped, and is a convenient way to pause fucking altogether,
or disable part of a complex pattern.
`Infinity` cycles forever.
Because JSON doesn't actually support the float `infinity`, use the string `"Infinity"`.

`motions` is an `array` of **Pattern**, **Stroke**, or **Wait** objects.
**Patterns** can be nested arbitrarily deep and made as long as desired.

##### Example **Pattern** JSON:

    {
      "cycles": "Infinity",
      "motions":
        [
          {
            "cycles": 3,
            "motions": [
              {"position": 0.69, "speed": 1},
              {"position": 0.42, "speed": 1},
              {"duration": 0.5}
            ]
          },
          {
            "cycles": 1,
            "motions": [
              {"position": 0.9, "speed": 0.2},
              {"duration": 0.1},
              {"position": 0.42, "speed": 0.2}
            ]
          }
        ]
    }

### Metadata

There is currently only one type of Metadata object.

#### **Query**

A **Query** replies to a client with the current state of fucking, as a **Query** object.
**Query** objects have two attributes, `pattern` and `stroke`.

Setting `pattern` to `true` will cause the reply to have this attribute set the current **Pattern** in use.

Setting `stroke` to `true` will cause the reply to set this attribute to the current **Stroke**.
A received `stroke` value of `null` means that the current pattern has run out and the machine isn't fucking.

##### Example **Query** JSON:

###### Sent:

`{"pattern": true, "stroke": true}`

###### Received:

`{"stroke": {"speed": 0.69, "position": 0.69}, "pattern": {"cycles": 5, "motions": [{"speed": 0.69, "position": 0.69}, {"duration": 1}, {"speed": 0.42, "position": 0.42}]}}`

Example JavaScript commands
---------------------------

Run these from a browser console.

#### Connect and log messages:

`websocket = new WebSocket("ws://localhost:6969", "openfuck");`

`websocket.onmessage = (message) => console.log(message.data);`

#### Send commands:

`websocket.send('{"cycles": 5, "motions": [{"position": 0.69, "speed": 0.69}, {"duration": 1}, {"position": 0.42, "speed": 0.42}]}')`

`websocket.send('{"pattern": true, "stroke": true}')`