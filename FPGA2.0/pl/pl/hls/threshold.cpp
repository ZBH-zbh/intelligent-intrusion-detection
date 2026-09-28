#include <ap_axi_sdata.h>
#include <hls_stream.h>
#include <ap_int.h>

typedef ap_axiu<32, 0, 0, 0> pixel_t;

void threshold(
    hls::stream<pixel_t>& in_stream,
    hls::stream<pixel_t>& out_stream,
    int width,
    int height,
    int thresh
) {
    #pragma HLS INTERFACE axis port=in_stream
    #pragma HLS INTERFACE axis port=out_stream
    #pragma HLS INTERFACE s_axilite port=width bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=height bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=thresh bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=return bundle=CTRL

    int total = width * height;

    for (int i = 0; i < total; i++) {
        #pragma HLS PIPELINE II=1
        pixel_t p = in_stream.read();

        ap_uint<8> val = p.data.range(7, 0);
        ap_uint<8> bin = (val > thresh) ? 255 : 0;

        pixel_t out;
        out.data  = bin;
        out.keep  = -1;
        out.strb  = -1;
        out.last  = p.last;

        out_stream.write(out);
    }
}
