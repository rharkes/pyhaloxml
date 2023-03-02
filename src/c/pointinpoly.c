// Simple c-code to determine if a point is inside a polygon.
#include <stdbool.h>
float min(float a, float b);
float max(float a, float b);
bool pointinpoly(float *point, float *polygon, int nvertices);

bool pointinpoly(float *point, float *polygon, int nvertices) {
    float p1x = 0.0;
    float p1y = 0.0;
    float p2x = 0.0;
    float p2y = 0.0;
    float xints = 0.0;
    int idx = 0;
    bool inside = false;
    p1x = polygon[0];
    p1y = polygon[1];
    for (int i = 0; i < (nvertices+1); ++i){
        idx = (i%nvertices)*2;
        p2x = polygon[idx];
        p2y = polygon[1+idx];
        if (point[1] > min(p1y, p2y)) {
            if (point[1] <= max(p1y, p2y)) {
                if (point[0] <= max(p1x,p2x)){
                    if (p1y != p2y){
                        xints = (point[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x;
                    }
                    if (p1x == p2x || point[0] <= xints){
                        inside = !inside;
                    }
                }
            }
        }
        p1x = p2x;
        p1y = p2y;
    }
    return inside;
}

float min(float a, float b){
    return (a>b)?b:a;
}
float max(float a, float b){
    return (a<b)?b:a;
}
