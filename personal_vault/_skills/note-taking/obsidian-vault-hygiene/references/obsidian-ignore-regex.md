# Obsidian userIgnoreFilters — reverse-engineered behavior

## Source: obsidian.asar (Obsidian app bundle)
Found at offset ~2289699 in `resources/obsidian.asar`:

```js
t.prototype.updateUserIgnoreFilters=function(){
  var e=this.app.vault.getConfig("userIgnoreFilters"),t=JSON.stringify(e);
  if(this.userIgnoreFiltersString!==t)
    if(this.userIgnoreFilterCache={},e)
      for(var n=this.userIgnoreFilters=[],i=0,r=e;i<r.length;i++){
        var o=r[i].trim();
        if(0!==o.length)try{
          o.length>2&&o.startsWith("/")&&o.endsWith("/")
            ?n.push(new RegExp(o.substring(1,o.length-1),"i"))      // DIRECTORY: substring, case-insensitive
            :n.push(new RegExp("^.*"+this.escapeRegExp(o)+".*$","i")); // GLOB: wrapped substring
        }catch(e){console.error("Bad regex for user ignore filter",e)}
      }
    else this.userIgnoreFilters=null
},
t.prototype.isUserIgnored=function(e){
  var t=this.userIgnoreFilters,n=this.userIgnoreFilterCache;
  if(!t)return!1;
  if(Object.hasOwn(n,e))return n[e];
  for(var i=!1,r=0,o=t;r<o.length;r++){if(o[r].test(e)){i=!0;break}}
  return n[e]=i,i
},
// triggered on config change:
t.prototype.onConfigChanged=function(e){"userIgnoreFilters"===e&&this.updateUserIgnoreFilters()}
```

## Behavior notes
- `isUserIgnored` is tested against the file/folder PATH (vault-relative, forward slashes).
- Folder container visibility: Obsidian's file explorer may still render a folder if it contains any non-ignored entry. A folder whose entire contents are ignored renders empty and is hidden. This is why a correct config can still "show" folders until re-index, and why dotfolder rename is the reliable fallback.
- Triggered on config change. If Obsidian is open while you edit app.json, it re-reads (may rewrite the file, preserving your patterns — format normalized but values intact).
- UI entry: Settings → Files & Links → "Excluded files" edits the SAME `userIgnoreFilters` array. Use it to nudge re-evaluation.
- Default value is `null` (not `[]`); Obsidian stores `null` when empty.
