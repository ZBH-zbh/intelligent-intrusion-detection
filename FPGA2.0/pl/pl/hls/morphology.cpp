#include <ap_axi_sdata.h>
#include <hls_stream.h>
#include <ap_int.h>

#define MAX_WIDTH 320

typedef ap_axiu<32, 0, 0, 0> pixel_t;

void morphology(
    hls::stream<pixel_t>& in_stream,
    hls::stream<pixel_t>& out_stream,
    int width,
    int height
) {
    #pragma HLS INTERFACE axis port=in_stream
    #pragma HLS INTERFACE axis port=out_stream
    #pragma HLS INTERFACE s_axilite port=width bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=height bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=return bundle=CTRL

    ap_uint<8> line_buf0[MAX_WIDTH];
    ap_uint<8> line_buf1[MAX_WIDTH];
    #pragma HLS BIND_STORAGE variable=line_buf0 type=ram_t2p
    #pragma HLS BIND_STORAGE variable=line_buf1 type=ram_t2p

    ap_uint<8> window[3][3];
    #pragma HLS ARRAY_PARTITION variable=window complete dim=0

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            #pragma HLS PIPELINE II=1
            pixel_t p = in_stream.read();
            ap_uint<8> val = p.data.range(7, 0);

            window[0][0] = window[0][1];
            window[0][1] = window[0][2];
            window[1][0] = window[1][1];
            window[1][1] = window[1][2];
            window[2][0] = window[2][1];
            window[2][1] = window[2][2];

            window[0][2] = line_buf0[x];
            window[1][2] = line_buf1[x];
            window[2][2] = val;

            line_buf0[x] = line_buf1[x];
            line_buf1[x] = val;

            ap_uint<8> out_val = 255;
            for (int i = 0; i < 3; i++) {
                #pragma HLS UNROLL
                for (int j = 0; j < 3; j++) {
                    #pragma HLS UNROLL
                    if (window[i][j] != 255) {
                        out_val = 0;
                    }
                }
            }

            bool valid = (y >= 2) && (x >= 2);

            pixel_t out;
            out.data  = valid ? out_val : ap_uint<8>(0);
            out.keep  = -1;
            out.strb  = -1;
            out.last  = p.last;

            out_stream.write(out);
        }
    }
}
