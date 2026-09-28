#include <ap_axi_sdata.h>
#include <hls_stream.h>
#include <ap_int.h>

#define MAX_WIDTH  320
#define MAX_HEIGHT 240
#define MAX_PIXELS (MAX_WIDTH * MAX_HEIGHT)

typedef ap_axiu<32, 0, 0, 0> pixel_t;

void frame_diff(
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

    static ap_uint<8> prev_frame[MAX_PIXELS];
    #pragma HLS BIND_STORAGE variable=prev_frame type=ram_t2p

    int total = width * height;

    for (int i = 0; i < total; i++) {
        #pragma HLS PIPELINE II=1
        pixel_t p = in_stream.read();

        ap_uint<8> curr = p.data.range(7, 0);
        ap_uint<8> prev = prev_frame[i];

        ap_uint<8> diff = (curr > prev) ? (curr - prev) : (prev - curr);

        pixel_t out;
        out.data  = diff;
        out.keep  = -1;
        out.strb  = -1;
        out.last  = p.last;

        out_stream.write(out);

        prev_frame[i] = curr;
    }
}
