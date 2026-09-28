#include <ap_axi_sdata.h>
#include <hls_stream.h>
#include <ap_int.h>

typedef ap_axiu<32, 0, 0, 0> pixel_t;

void rgb2gray(
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

    int total = width * height;

    for (int i = 0; i < total; i++) {
        #pragma HLS PIPELINE II=1
        pixel_t p = in_stream.read();

        ap_uint<8> r = p.data.range(23, 16);
        ap_uint<8> g = p.data.range(15, 8);
        ap_uint<8> b = p.data.range(7, 0);

        ap_uint<8> gray = (r * 76 + g * 150 + b * 29) >> 8;

        pixel_t out;
        out.data  = gray;
        out.keep  = -1;
        out.strb  = -1;
        out.last  = p.last;

        out_stream.write(out);
    }
}
