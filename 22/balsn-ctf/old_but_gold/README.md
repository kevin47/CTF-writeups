## Old but gold

- The core of this challenge is padding oracle attack on AES CFB with a little twist, I call it JSON oracle attack
- The first key is the unpad function, controlling the last byte enable us to control the length of the plaintext
- The second key is the json unmarshal function, if we unmarshal `{}`, it will actually success without any error. If we insert arbitrary number of spaces between the curly brackets `{     }`, the same still stands
- Combining the two keys, we get a padding oracle where we control the plaintext into `{ X` and guess the `X`, we get 200 with "User not found" if the `X` become `}`, 400 for anything else
- One thing to note is that for the blocks other than the first one, we actually have to brute force the first two bytes `XX` together to get `{}`, so that's 65536 connections required. It will be a little bit slow on remote server due to the network latency, but parallelizing easily solve this
