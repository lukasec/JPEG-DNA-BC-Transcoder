# Updates and ongoing work

## Ongoing work

- Constrained Shannon Fano entropy coder (testing phase)
- Thumbnail-specific encoder (testing phase)

- Consensus for noised formatted oligos (conception)
- Noise model (implementation)
- Transcoder JPEG -> JPEG DNA (and revert) (implementation)
- Error correction codes(conception)

## 07/06/22

- Overheads for quantization tables

## 12/06/21

- Edge padding
- Common format for RGB and gray level, no prior needed on the type of image (RGB or gray) to decode.
- Fix to make the code not break when a noised codeword is out of the codebook.
- Synchronisation to next block when a huffman code is not decodable
