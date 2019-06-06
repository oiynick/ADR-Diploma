f = waitbar(0, 'Starting calculations...');

st_t = datetime('now');

x = 1/1600;
done = 0;

fmt = '%.3f';
lon_f = zeros(1600, 315361);
lat_f = zeros(1600, 315361);

for i = 1:32
    for k = 1:50
        for j = 1:315361
            lon_f((i-1)*32+k, j) = lon(i, k, j)*180/pi;
            lat_f((i-1)*32+k, j) = lat(i, k, j)*180/pi;
        end
        done = done + x;
        p = round(done*100);
        pt = datetime('now') - st_t;
        string = [char(pt), ' passed, ', char(p), '% done'];
        waitbar(done, f, string)
    end
end

close(f)