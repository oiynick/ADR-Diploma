f = waitbar(0, 'Starting calculations...');

st_t = datetime('now');
flat = fopen('lat.txt', 'w');
flon = fopen('lon.txt', 'w');

x = 1/315361;
done = 0;

fmt = '%.3f';

for i = 1:315361
    for j = 1:1600
        fprintf(flon, fmt, lon_f(j, i));
        fprintf(flat, fmt, lat_f(j, i));
        if j ~= 1600
            fprintf(flat, '\t');
            fprintf(flon, '\t');
        end
    end
    fprintf(flon, '\n');
    fprintf(flat, '\n');
    done = done + x;
    pt = datetime('now') - st_t;
    string = [char(pt), ' passed, ', sprintf('%.2f', done*100), '% done'];
    waitbar(done, f, string)
end

close(flat)
close(flon)
close(f)