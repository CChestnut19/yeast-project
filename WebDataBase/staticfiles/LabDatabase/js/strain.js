(() => {
    const tab = document.getElementById('strain-tab');
    const tableBody = document.getElementById('strainTableBody');
    if (!tab || !tableBody) return;

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    const emptyState = document.getElementById('strainEmpty');
    const searchInput = document.getElementById('strainSearchInput');
    let loaded = false;

    const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));

    async function api(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                ...(options.headers || {})
            }
        });
        const result = await response.json();
        if (!response.ok || result.success === false) {
            throw new Error(result.message || `请求失败 (${response.status})`);
        }
        return result;
    }

    function genotypeHtml(genotypes) {
        if (!genotypes?.length) return '<span class="text-muted">-</span>';
        return `<div class="strain-genotypes">${genotypes.map(item => `
            <span class="strain-genotype">
                ${escapeHtml(item.plasmidname)} (#${item.plasmidid})
                <button type="button" title="删除关联" data-action="delete-genotype" data-sgid="${item.sgid}">×</button>
            </span>`).join('')}</div>`;
    }

    function render(strains) {
        emptyState.style.display = strains.length ? 'none' : 'block';
        tableBody.innerHTML = strains.map(item => `
            <tr>
                <td>${item.strainid}</td>
                <td>${escapeHtml(item.strainname)}</td>
                <td>${escapeHtml(item.background)}</td>
                <td>${escapeHtml(item.marker)}</td>
                <td>${escapeHtml(item.store)}</td>
                <td>${genotypeHtml(item.genotypes)}</td>
                <td>
                    <div class="strain-actions">
                        <button class="btn btn-sm btn-outline-primary" type="button" data-action="edit" data-id="${item.strainid}">编辑</button>
                        <button class="btn btn-sm btn-outline-secondary" type="button" data-action="add-genotype" data-id="${item.strainid}">关联 Plasmid</button>
                        <button class="btn btn-sm btn-outline-danger" type="button" data-action="delete" data-id="${item.strainid}">删除</button>
                    </div>
                </td>
            </tr>`).join('');
    }

    async function loadStrains() {
        try {
            const search = encodeURIComponent(searchInput.value.trim());
            const result = await api(`/LabDatabase/api/strains?search=${search}`);
            render(result.data || []);
            loaded = true;
        } catch (error) {
            alert(error.message);
        }
    }

    async function pollStrainUpload(taskId) {
        const timer = window.setInterval(async () => {
            try {
                const result = await api(`/LabDatabase/task_status/${taskId}`);
                if (result.status === 'completed') {
                    window.clearInterval(timer);
                    alert(result.message || 'Strain 文件处理完成');
                    await loadStrains();
                } else if (result.status === 'failed') {
                    window.clearInterval(timer);
                    alert(result.message || result.error || 'Strain 文件处理失败');
                }
            } catch (error) {
                window.clearInterval(timer);
                alert(error.message);
            }
        }, 2000);
    }

    function openStrainDialog(strain = null) {
        const dialog = document.createElement('dialog');
        dialog.className = 'strain-dialog';
        dialog.innerHTML = `
            <form class="strain-form">
                <h5>${strain ? '编辑' : '新增'} Strain</h5>
                <label>名称<input class="form-control" name="strainname" maxlength="20" required value="${escapeHtml(strain?.strainname || '')}"></label>
                <label>Background<input class="form-control" name="background" maxlength="20" required value="${escapeHtml(strain?.background || '')}"></label>
                <label>Marker<input class="form-control" name="marker" maxlength="30" required value="${escapeHtml(strain?.marker || '')}"></label>
                <label>Store<input class="form-control" name="store" maxlength="100" required value="${escapeHtml(strain?.store || '')}"></label>
                <div class="strain-form-actions">
                    <button class="btn btn-outline-secondary" type="button" data-close>取消</button>
                    <button class="btn btn-primary" type="submit">保存</button>
                </div>
            </form>`;
        document.body.appendChild(dialog);
        dialog.querySelector('[data-close]').onclick = () => dialog.close();
        dialog.addEventListener('close', () => dialog.remove());
        dialog.querySelector('form').onsubmit = async event => {
            event.preventDefault();
            const data = Object.fromEntries(new FormData(event.currentTarget));
            try {
                await api(
                    strain ? `/LabDatabase/api/strains/${strain.strainid}` : '/LabDatabase/api/strains',
                    {method: strain ? 'PUT' : 'POST', body: JSON.stringify(data)}
                );
                dialog.close();
                await loadStrains();
            } catch (error) {
                alert(error.message);
            }
        };
        dialog.showModal();
    }

    tab.addEventListener('shown.bs.tab', () => {
        if (!loaded) loadStrains();
    });
    document.getElementById('strainCreateButton').onclick = () => openStrainDialog();
    document.getElementById('strainSearchButton').onclick = loadStrains;
    document.getElementById('strainFileUploadButton').onclick = async () => {
        const fileInput = document.getElementById('strainFileInput');
        const file = fileInput.files[0];
        if (!file) {
            alert('请选择 Strain Excel 文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('/LabDatabase/UploadFile', {
                method: 'POST',
                body: formData,
                headers: {'X-CSRFToken': csrfToken}
            });
            const result = await response.json();
            if (!response.ok || result.success === false) {
                throw new Error(result.message || 'Strain 文件上传失败');
            }
            bootstrap.Modal.getOrCreateInstance(
                document.getElementById('strainUploadModal')
            ).hide();
            fileInput.value = '';
            if (result.task_id) {
                pollStrainUpload(result.task_id);
            } else {
                alert(result.message || '上传成功，数据处理中');
            }
            loaded = false;
        } catch (error) {
            alert(error.message);
        }
    };
    searchInput.addEventListener('keydown', event => {
        if (event.key === 'Enter') loadStrains();
    });

    tableBody.addEventListener('click', async event => {
        const button = event.target.closest('[data-action]');
        if (!button) return;
        const action = button.dataset.action;
        try {
            if (action === 'edit') {
                const result = await api(`/LabDatabase/api/strains/${button.dataset.id}`);
                openStrainDialog(result.data);
            } else if (action === 'delete') {
                if (confirm('确定删除该 Strain 及其全部 genotype 关联吗？')) {
                    await api(`/LabDatabase/api/strains/${button.dataset.id}`, {method: 'DELETE'});
                    await loadStrains();
                }
            } else if (action === 'add-genotype') {
                const plasmidid = prompt('请输入要关联的 Plasmid ID');
                if (plasmidid) {
                    await api('/LabDatabase/api/strain-genotypes', {
                        method: 'POST',
                        body: JSON.stringify({strainid: Number(button.dataset.id), plasmidid: Number(plasmidid)})
                    });
                    await loadStrains();
                }
            } else if (action === 'delete-genotype') {
                if (confirm('确定删除该 genotype 关联吗？')) {
                    await api(`/LabDatabase/api/strain-genotypes/${button.dataset.sgid}`, {method: 'DELETE'});
                    await loadStrains();
                }
            }
        } catch (error) {
            alert(error.message);
        }
    });
})();
