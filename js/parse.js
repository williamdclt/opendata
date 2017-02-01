function parse(callback) {
    d3.json("collection/collection.json",function (error, data) {
        if (error) throw error;

        callback(data);
    });
}
