function main(data_raw){
    let newData = (data_raw.replace(/&quot;/g, '')).split(', ');
    newData = (newData[2].replace(/]/g, '')).replace(/&#x27;/g, "");
    return newData;
}

let data = "&quot;, &quot;stderr_lines&quot;: [&quot;&quot;, &quot;Error: VM &#x27;CSM1KPOCVMW9334&#x27; not found in inventory.&quot;], &quot;stdout&quot;: &quot;&quot;, &quot;stdout_lines&quot;: []}</span>\n\nTASK [n8n_assist : get_vm_tag | Handle errors] *********************************\n<span class=\"ansi32\">ok: [localhost] =&gt; {</span>\n<span class=\"ansi32\">    &quot;msg&quot;: &quot;Error occurred while retrieving VM tag:\\"
console.log(main(data));