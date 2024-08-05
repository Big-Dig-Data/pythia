function setFilterCounts(filtersObj, filterCountsObj) {
  let filterTypes = []
  for (let f in filterCountsObj) {
    filterTypes.push(f)
  }
  for (let f of filtersObj) {
    filterCountsObj[f.name] = f.id.length;
    filterTypes.splice(filterTypes.indexOf(f.name), 1);
  }
  filterTypes.forEach((el) => {
    filterCountsObj[el] = 0;
  });
}

export { setFilterCounts }
